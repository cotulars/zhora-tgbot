from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums.chat_type import ChatType

from src.app import dp, bot, openai_client
from src.database.domain.bot_settings_db import BotSettingsDB

from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB
from src.utils.chatgpt_utils import generate_message_context
from src.utils.telegraph_utils import create_telegra_article

# Create a router for commands
router = Router()
dp.include_router(router)

@router.message(Command("sum"), F.chat.type.in_({"group", "supergroup"}))
async def summary_cmd(message: Message):
    msg = await message.reply("Выполняется...")

    args = message.text.split(" ")

    if len(args) > 1:
        count = int(args[1])
    else:
        count = 500

    context = await generate_message_context(message.chat.id, count=count, tag='summary')

    with open("./src/assets/prompts/summary_prompt.txt", "r") as f:
        prompt = f.read()
        response = await openai_client.responses.create(
            model=BotSettingsDB.get_setting("summary_model") or "gpt-5-nano",
            input=[
                {
                    "role": "developer",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": context
                        }
                    ]
                }
            ],
            text={
                "format": {
                    "type": "text"
                },
                "verbosity": "medium"
            },
            reasoning={
                "effort": "medium",
                "summary": None
            },
        )

        article_url = await create_telegra_article(
                title=f"Summary {message.date.strftime('%Y-%m-%d %H:%M')}",
                html_content=response.output_text
            )
        if article_url:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text=f'{article_url}'
            )
        else:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text="Не удалось создать статью"
            )

print("Summary command loaded")
