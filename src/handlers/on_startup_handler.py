import os

from aiogram import Bot

from src.database.domain.chats_db import ChatsDB


async def on_startup(bot: Bot):
    chats = await ChatsDB.get_all_chats()

    if os.path.exists('./src/assets/__update_flag__'):
        with open('./src/assets/release_notes.txt', "r") as f:
            release_notes = f.read()
            for chat in chats:
                chat_id = chat.id
                await bot.send_message(chat_id, release_notes)

        os.remove('./src/assets/__update_flag__')