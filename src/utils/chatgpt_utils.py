import asyncio
import base64
import json
import tempfile
import time

from google.genai import types

from src.app import openai_client, bot, gemini_client
from src.database.domain.chats_db import ChatsDB
from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB
from src.database.model.chat_entity import Chat

cotext_caching = {}

def get_message_dict(msg):
    message_dict = {
        'message_id': msg.msg_id,
        'from_user_id': msg.user_id,
        'date': str(msg.date)
    }

    if msg.text:
        message_dict['message_text'] = msg.text

    if msg.reply_to_msg_id:
        message_dict['reply_to'] = msg.reply_to_msg_id
        if msg.quote_from_reply:
            message_dict['quote_from_reply'] = msg.quote_from_reply

    if msg.is_forwarded:
        message_dict['is_forward'] = True
        message_dict['forward_from'] = msg.forward_from

    if msg.is_sticker:
        message_dict['is_sticker'] = True
        message_dict['sticker_description'] = msg.sticker_description

    if msg.media_content_type:
        message_dict['media_content_type'] = msg.media_content_type
        message_dict['media_content_description'] = msg.media_content_description
        message_dict['media_content_id'] = msg.media_content_id

    if msg.is_voice:
        message_dict['is_voice'] = True
        message_dict['voice_description'] = msg.voice_description

    if msg.have_url:
        message_dict['contains_url'] = True
        message_dict['url_content_description'] = msg.url_content_description
        message_dict['url_from_message'] = msg.url_raw

    return message_dict


async def generate_message_context(chat_id, count = 100, tag='default', threshold=100) -> str:

    if cotext_caching.get(tag, None):
        messages = await MessagesDB.get_messages_from_msg_id_to_latest(chat_id, cotext_caching[tag])
        if len(messages) > (threshold+count):
            messages = await MessagesDB.get_messages(chat_id=chat_id, count=count)
            cotext_caching[tag] = messages[0].msg_id
    else:
        messages = await MessagesDB.get_messages(chat_id=chat_id, count=count)
        cotext_caching[tag] = messages[0].msg_id


    members_list = []
    messages_list = []

    for msg in messages:
        message_dict = get_message_dict(msg)
        messages_list.append(message_dict)

    users_db = UsersDB()
    users = await UsersDB.get_users_from_chat(chat_id)

    for user_id in users:
        user = await users_db.get_user(user_id)

        user_dict = {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'is_activated': user.is_activated,
            'date_of_birth' : None,
            'bio': None
        }

        members_list.append(user_dict)

    await users_db.close()

    chat_raw_info: Chat = await ChatsDB.get_chat_info(chat_id)

    chat_info = {
        'id': chat_id,
        'title': chat_raw_info.title,
        'members_count': chat_raw_info.members_count,
        'description': None,
    }

    response = {
        'chat_info': chat_info,
        'members': members_list,
        'messages': messages_list
    }

    return json.dumps(response, ensure_ascii=False)

async def generate_photo_description(photo_id) -> str:
    file = await bot.get_file(photo_id)
    photo_file = await bot.download(file=file)
    photo_bytes = photo_file.getvalue()
    photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')

    with open(f"./src/assets/prompts/photo_description_prompt.txt", "r") as f:
        prompt = f.read()
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Photo ID: {photo_id}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{photo_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        return response.choices[0].message.content

async def generate_voice_description(voice_id) -> str:
    file = await bot.get_file(voice_id)
    voice_bytes = await bot.download(file=file)

    with tempfile.NamedTemporaryFile(suffix=".ogg") as temp_audio:
        temp_audio.write(voice_bytes.getvalue())
        temp_audio.flush()
        with open(temp_audio.name, "rb") as data:
            transcription = await openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=data
            )

    return transcription.text

async def generate_sticker_description(chat_id, sticker_id) -> str:
    return 'Nothing'

async def generate_url_description(url) -> str:
    return 'Nothing'

async def wait_for_file_active(client, file_name: str, timeout: float = 30.0, interval: float = 1.0):
    start_time = time.time()
    while True:
        info = await client.aio.files.get(name=file_name)
        state = info.state
        if state == "ACTIVE":
            return
        if state in ("FAILED", "ARCHIVED"):
            raise RuntimeError(f"Не удалось загрузить файл: состояние {state}")
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Файл {file_name} не активировался в течение {timeout} секунд")
        await asyncio.sleep(interval)

async def generate_video_description(video_id) -> str:
    file = await bot.get_file(video_id)
    video_file = await bot.download(file=file)
    uploaded_video_file = await gemini_client.aio.files.upload(file=video_file, config=types.UploadFileConfig(mime_type="video/mp4"))

    try:
        await wait_for_file_active(gemini_client, uploaded_video_file.name)

        with open(f"./src/assets/prompts/video_description_prompt.txt", "r") as f:
            prompt = f.read()
            response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=prompt
                ),
                contents=[
                    uploaded_video_file,
                ]
            )
        await gemini_client.aio.files.delete(name=uploaded_video_file.name)

        return response.text
    except Exception as e:
        print(f'Error: {e}')
        return 'Video not described'

async def generate_document_description(document_id) -> str:
    file = await bot.get_file(document_id)
    document_file = await bot.download(file.file_path)

    return 'Nothing'

async def generate_audio_description(audio_id) -> str:
    file = await bot.get_file(audio_id)
    audio_file = await bot.download(file=file)
    uploaded_audio_file = await gemini_client.aio.files.upload(file=audio_file,
                                                               config=types.UploadFileConfig(mime_type="video/mp4"))

    try:
        await wait_for_file_active(gemini_client, uploaded_audio_file.name)

        with open(f"./src/assets/prompts/audio_description_prompt.txt", "r") as f:
            prompt = f.read()
            response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=prompt
                ),
                contents=[
                    uploaded_audio_file,
                ]
            )
        await gemini_client.aio.files.delete(name=uploaded_audio_file.name)

        return response.text
    except Exception as e:
        print(f'Error: {e}')
        return 'Audio not described'