import asyncio
import logging

from src.app import bot, dp, redis_client
from src.database.database_main import init_db
from src.database.domain.users_db import UsersDB
from src.database.model.user_entity import User
from src.handlers import *
from src.commands import *
from src.handlers.on_startup_handler import on_startup
from src.menus import *
from src.patches import *

async def init():
    await init_db()
    print("Database inited")
    await on_startup(bot)

async def main():
    logging.basicConfig(level=logging.ERROR)

    await init()
    print("Bot is running... ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
