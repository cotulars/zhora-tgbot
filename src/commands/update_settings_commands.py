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

@router.message(Command("update_settings"), F.chat.type.in_({"group", "supergroup"}))
async def update_settings(message: Message):
    await message.delete()
    try:
        await BotSettingsDB.load_settings()
    except Exception as e:
        bot.send_message(chat_id=message.chat.id, message=f"Failed to load settings: {e}")


print("Settings commands loaded")
