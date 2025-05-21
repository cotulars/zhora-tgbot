from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.menus.settings.settings_main import menu_settings_main
from src.app import dp

router = Router()
dp.include_router(router)

@router.message(Command("settings"))
async def help_cmd(message: Message):
    await menu_settings_main(chat_id=message.chat.id)

print("Settings command loaded")
