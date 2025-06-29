import re
from contextlib import asynccontextmanager

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums.chat_type import ChatType

from src.app import dp, bot, openai_client, redis_client
from src.database.domain.bot_settings_db import BotSettingsDB
from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB
from src.utils.chatgpt_utils import generate_message_context, get_message_dict

# Create a router for commands
router = Router()
dp.include_router(router)

@asynccontextmanager
async def user_parallel_limit(user_id: int):
    key = f"user:{user_id}:active"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)  # тайм-аут, чтобы зомби-ключи не оставались

    try:
        if count > 1:
            yield False
        else:
            yield True
    finally:
        await redis_client.decr(key)


async def ask_zhora_command(message: Message):
    try:
        bot.send_chat_action(message.chat.id, "typing")

        context = await generate_message_context(message.chat.id, count=60, tag='ask_zhora', threshold=40)

        with open("./src/assets/prompts/ask_prompt.txt", "r") as f:
            prompt = f.read()
            if BotSettingsDB.get_setting("is_thinking_model") != "True":
                response = await openai_client.responses.create(
                    model=BotSettingsDB.get_setting("bot_model") or "gpt-4.1-mini",
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
                                    "text": f"{context}"
                                }
                            ]
                        }
                    ],
                    text={
                        "format": {
                            "type": "text"
                        }
                    },
                    reasoning={
                        "effort": "medium",
                        "summary": "auto"
                    },
                    temperature=0.8,
                    max_completion_tokens=2000,
                    tools=[
                        {
                            "type": "web_search_preview",
                            "user_location": {
                                "type": "approximate"
                            },
                            "search_context_size": "medium"
                        }
                    ],
                    user=f"{message.from_user.id}",
                    metadata={
                        "type": "group_conversation",
                        "chat": f"{message.chat.id}",
                        "user": f"{message.from_user.id}"
                    },
                    store=True
                )

            else:
                response = await openai_client.responses.create(
                    model=BotSettingsDB.get_setting("bot_model"),
                    messages=[
                        {
                            "role": "developer",
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
                                    "text": f"{context}"
                                }
                            ]
                        }
                    ],
                    text={
                        "format": {
                            "type": "text"
                        }
                    },
                    reasoning={
                        "effort": "medium",
                        "summary": None
                    },
                    tools=[
                        {
                            "type": "web_search_preview",
                            "user_location": {
                                "type": "approximate"
                            },
                            "search_context_size": "medium"
                        }
                    ],
                    user=f"{message.from_user.id}",
                    metadata={
                        "type": "group_conversation",
                        "chat": f"{message.chat.id}",
                        "user": f"{message.from_user.id}"
                    },
                    store=True
                )

            resp: str = response.text

            await message.reply(resp)

    except Exception as e:
        await message.reply("Something went wrong. Error:\n\n" + str(e))


@router.message(Command("zhora"), F.chat.type.in_({"group", "supergroup"}))
async def ask_zhora_cmd(message: Message):
    async with user_parallel_limit(message.from_user.id) as allowed:
        if not allowed:
            await message.reply("Слишком много одновременных запросов. Подождите.")
            return
        await ask_zhora_command(message)


@router.message(F.text.regexp(r"^жора.*", flags=re.IGNORECASE), F.chat.type.in_({"group", "supergroup"}))
async def ask_zhora_regex_cmd(message: Message):
    async with user_parallel_limit(message.from_user.id) as allowed:
        if not allowed:
            await message.reply("Слишком много одновременных запросов. Подождите.")
            return
        await ask_zhora_command(message)

@router.message(F.captions.regexp(r"^жора.*", flags=re.IGNORECASE), F.chat.type.in_({"group", "supergroup"}))
async def ask_zhora_regex_cmd_captions(message: Message):
    async with user_parallel_limit(message.from_user.id) as allowed:
        if not allowed:
            await message.reply("Слишком много одновременных запросов. Подождите.")
            return
        await ask_zhora_command(message)

@router.message(F.reply_to_message, F.chat.type.in_({"group", "supergroup"}))
async def ask_zhora_reply_cmd(message: Message):
    # Check if the message is a reply to a message from the bot
    if message.reply_to_message.from_user.id != bot.id:
        return

    async with user_parallel_limit(message.from_user.id) as allowed:
        if not allowed:
            await message.reply("Слишком много одновременных запросов. Подождите.")
            return
        await ask_zhora_command(message)


print("Ask zhora command loaded")
