from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from src.app import dp, bot
from src.database.domain.users_db import UsersDB

# Create a router for commands
router = Router()
dp.include_router(router)

@router.message(Command("all"), F.chat.type.in_({"group", "supergroup"}))
async def all_cmd(message: Message):
    await message.delete()

    db = UsersDB()
    users_to_tag = await UsersDB.get_users_from_chat(message.chat.id)

    usernames = []

    for user_id in users_to_tag:
        user = await db.get_user(user_id)
        if user.username:
            usernames.append(f"@{(await db.get_user(user_id)).username}")


    await bot.send_message(message.chat.id, f"Tagging {len(usernames)} users:\n\n" + "\n".join(usernames))

print("All command loaded")
