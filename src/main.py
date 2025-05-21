import asyncio
import logging

from src.app import bot, dp
from src.database.database_main import init_db
from src.database.domain.users_db import UsersDB
from src.database.model.user_entity import User

async def init():
    await init_db()
    if not await UsersDB.is_user_exists(bot.id):
        udb = UsersDB()
        await udb.add_user(
            User(
                id=bot.id,
                username="ME",
                name="ME",
                is_activated=True
            )
        )
        await udb.close()
    print("Database inited")

async def main():
    logging.basicConfig(level=logging.WARN)

    await init()
    print("Bot is running... ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    from src.handlers import *
    from src.commands import *
    from src.menus import *
    from src.patches import *
    asyncio.run(main())
