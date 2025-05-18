from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.app import dp

# Create a router for commands
router = Router()
dp.include_router(router)

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.reply("Hi! I'm a simple bot to send you the latest news from the web.")

print("Help command loaded")
