from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums.chat_type import ChatType

from src.app import dp, bot, openai_client

from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB
from src.utils.chatgpt_utils import generate_message_context
from src.utils.telegraph_utils import create_telegra_article

# Create a router for commands
router = Router()
dp.include_router(router)

@router.message(Command("sum"), F.chat.type.in_({"group", "supergroup"}))
async def summary_cmd(message: Message):
    context = await generate_message_context(message.chat.id, count=500, tag='summary')

    msg = await message.reply("Выполняется...")

    with open("./src/prompts/summary_prompt.txt", "r") as f:
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
                            "text": context
                        }
                    ]
                }
            ],
            response_format={
                "type": "text"
            },
            temperature=0.2,
            max_completion_tokens=5000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        print(response.choices[0].message.content)

        article_url = await create_telegra_article(
                title=f"Summary {message.date.strftime('%Y-%m-%d %H:%M')}",
                html_content=response.choices[0].message.content
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
