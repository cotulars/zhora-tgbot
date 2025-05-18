from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.app import dp
from src.database.domain.users_db import UsersDB
from src.database.model.user_entity import User

# Create a router for commands
router = Router()
dp.include_router(router)

@router.message(Command("start"))
async def start_cmd(message: Message):
    db = UsersDB()
    user = await db.get_user(message.from_user.id, no_cache=True)
    if not user:
        await db.add_user(
            User(
                id=message.from_user.id,
                username=message.from_user.username,
                name=f'{message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name else ""}',
                is_activated=True
            )
        )
        await message.reply("Привет я Жора. Меня заставляют читать чат и писать самари, но мне нравится!")
    else:
        if user.is_activated: 
            await message.reply("Уже знакомы")
        else:
            user.is_activated = True
            await db.commit()
            await message.reply("Будем знакомы")

    await db.close()

print("Start command loaded")
