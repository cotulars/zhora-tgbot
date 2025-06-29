import asyncio
import logging

from src.app import bot, dp
from src.database.database_main import init_db
from src.database.domain.bot_settings_db import BotSettingsDB
from src.handlers import *
from src.commands import *
from src.handlers.on_startup_handler import on_startup
from src.menus import *
from src.patches import *

async def init():
    await init_db()
    await BotSettingsDB.load_settings()
    print("Database inited")
    await on_startup(bot)

async def main():
    logging.basicConfig(level=logging.ERROR)

    await init()
    print("Bot is running... ✅")
    await dp.start_polling(bot, tasks_concurrency_limit=10)


if __name__ == "__main__":
    asyncio.run(main())
