from datetime import timezone
from typing import Optional

from src.app import dp, bot
from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB
from src.database.model.message_entity import Message
from src.database.model.user_entity import User

from aiogram.types import Update, Message as TgMessage
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from src.utils.chatgpt_utils import generate_photo_description, generate_video_description, \
    generate_audio_description, generate_sticker_description, generate_voice_description, generate_document_description


async def on_group_message(msg: TgMessage):
    naive_utc_date = msg.date.astimezone(timezone.utc).replace(tzinfo=None)

    chat_id = msg.chat.id

    message_text: Optional[str] = None
    media_content_type: Optional[str] = None
    media_content_description: Optional[str] = None
    media_content_id: Optional[str] = None

    sticker_description: Optional[str] = None

    have_url = False
    url_content_description: Optional[str] = None
    url_raw: Optional[str] = None

    voice_description: Optional[str] = None

    is_forwarded = False
    forward_from: Optional[str] = None

    if msg.text:
        message_text = msg.text
        if msg.entities:
            for entity in msg.entities:
                if entity.type == "url":
                    have_url = True
                    url_raw = entity.url
                    url_content_description = entity.url
                    break
                elif entity.type == "text_link":
                    have_url = True
                    url_raw = entity.url
                    url_content_description = entity.url
                    break

    if msg.photo:
        if msg.caption:
            message_text = msg.caption
        media_content_type = "photo"
        media_content_id = msg.photo[-1].file_id
        media_content_description = await generate_photo_description(msg.photo[-1].file_id)
    elif msg.video:
        if msg.caption:
            message_text = msg.caption
        media_content_type = "video"
        media_content_id = msg.video.file_id
        media_content_description = await generate_video_description(msg.video.file_id)
    elif msg.audio:
        if msg.caption:
            message_text = msg.caption
        media_content_type = "audio"
        media_content_id = msg.audio.file_id
        media_content_description = await generate_audio_description(msg.audio.file_id)
    elif msg.document:
        if msg.caption:
            message_text = msg.caption
        media_content_type = "document"
        media_content_id = msg.document.file_id
        media_content_description = await generate_document_description(msg.document.file_id)

    if msg.sticker:
        sticker_description = await generate_sticker_description(chat_id, msg.sticker.file_id)

    if msg.voice:
        voice_description = await generate_voice_description(msg.voice.file_id)

    if msg.forward_from or msg.forward_from_chat or msg.forward_sender_name or msg.forward_from_message_id:
        is_forwarded = True
        if msg.forward_from:
            forward_from = msg.forward_from.full_name
        elif msg.forward_from_chat:
            forward_from = msg.forward_from_chat.title
        elif msg.forward_sender_name:
            forward_from = msg.forward_sender_name
        elif msg.forward_from_message_id:
            forward_from = f"Message {msg.forward_from_message_id}"
        else:
            forward_from = "Unknown"

    await MessagesDB.add_message(
        Message(
            chat_id=msg.chat.id,
            msg_id=msg.message_id,
            user_id=msg.from_user.id,
            text=message_text,
            reply_to_msg_id=msg.reply_to_message.message_id if msg.reply_to_message else None,
            quote_from_reply=msg.quote.text if msg.quote else None,
            media_content_type=media_content_type,
            media_content_description = media_content_description,
            media_content_id = media_content_id,
            is_forwarded = is_forwarded,
            forward_from = forward_from,
            is_sticker = True if msg.sticker else False,
            sticker_description = sticker_description,
            is_voice = True if msg.voice else False,
            voice_description=voice_description,
            have_url = have_url,
            url_content_description = url_content_description,
            url_raw = url_raw,
            date=naive_utc_date
        )
    )


class PersistAllMessagesMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        if event.message and event.message.chat.type in {"group", "supergroup"}:
            msg = event.message

            if (event.message.new_chat_members
                    and (bot.id in [member.id for member in event.message.new_chat_members])):
                return await handler(event, data)

            if msg.from_user.id == 867166409:
                return []

            if not await UsersDB.is_user_exists(msg.from_user.id):
                udb = UsersDB()
                await udb.add_user(
                    User(
                        id=msg.from_user.id,
                        username=msg.from_user.username,
                        name=msg.from_user.full_name,
                    )
                )
                await udb.close()

            if msg.chat.type not in {"group", "supergroup"}:
                return await handler(event, data)

            await on_group_message(msg)
        return await handler(event, data)

dp.update.middleware(PersistAllMessagesMiddleware())

print("On group message handler loaded")
