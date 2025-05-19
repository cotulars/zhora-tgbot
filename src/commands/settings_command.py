from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from menus.settings.settings_main import menu_settings_main
from src.app import dp

# Create a router for commands
router = Router()
dp.include_router(router)

@router.message(Command("help"))
async def help_cmd(message: Message):
    await menu_settings_main(message.chat.id, message.from_user.id)

print("Settings command loaded")
