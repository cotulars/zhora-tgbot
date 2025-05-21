import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums.chat_type import ChatType

from src.app import dp, bot, openai_client
from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB
from src.utils.chatgpt_utils import generate_message_context

# Create a router for commands
router = Router()
dp.include_router(router)

async def ask_zhora_command(message: Message):
    context = await generate_message_context(message.chat.id, count=60, tag='ask_zhora', threshold=40)

    text = f'From: {message.from_user.full_name} ({message.from_user.username}) {message.from_user.id}\nUser request:\n"{message.text}"\n'

    if message.reply_to_message:
        text += f'reply to: {message.reply_to_message.message_id if message.reply_to_message else ""}'

    with open("./src/assets/prompts/ask_prompt.txt", "r") as f:
        prompt = f.read()
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
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
                            "text": f"60-100 messages context:\n\n"
                                    f"{context}"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ],
            response_format={
                "type": "text"
            },
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        await message.reply(response.choices[0].message.content)


@router.message(Command("zhora"), F.chat.type.in_({"group", "supergroup"}))
async def ask_zhora_cmd(message: Message):
    await ask_zhora_command(message)

@router.message(F.text.regexp(r"^жора ", flags=re.IGNORECASE), F.chat.type.in_({"group", "supergroup"}))
async def ask_zhora_regex_cmd(message: Message):
    await ask_zhora_command(message)

@router.message(F.reply_to_message, F.chat.type.in_({"group", "supergroup"}))
async def ask_zhora_reply_cmd(message: Message):
    # Check if the message is a reply to a message from the bot
    if message.reply_to_message.from_user.id != bot.id:
        return
    await ask_zhora_command(message)

print("Ask zhora command loaded")
