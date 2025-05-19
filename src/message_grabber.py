from datetime import timezone

from telethon import TelegramClient, events
from telethon.tl.custom.message import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import async_session

from src.config import API_ID, API_HASH
from src.database.database_main import init_db
from src.database.domain.users_db import UsersDB
from src.database.model.message_entity import Message as DBMessage
from src.database.model.user_entity import User

session_name = 'anon'  # путь до .session-файла юзербота

client = TelegramClient(session_name, API_ID, API_HASH)

async def fetch_and_store_messages(chat_id: int, limit: int = 10000):
    await init_db()

    a = 1

    message: Message
    async for message in client.iter_messages(chat_id, limit=limit):
        if not message.text:  # игнор пустых (можно убрать)
            continue

        print(f"Message {a}/10000")

        naive_utc_date = message.date.astimezone(timezone.utc).replace(tzinfo=None)

        udb = UsersDB()

        if not await UsersDB.is_user_exists(message.sender_id):
            await udb.add_user(
                User(
                    id=message.sender_id,
                    username=message.sender.username,
                    name=f'{message.sender.first_name} {message.sender.last_name if message.sender.last_name else ""}'
                )
            )

        await udb.close()

        async with async_session() as session:
            msg = DBMessage(
                msg_id=message.id,
                chat_id=message.chat_id,
                user_id=message.sender_id,
                text=message.text,
                reply_to_msg_id=message.reply_to_msg_id,
                date=naive_utc_date
            )
            session.add(msg)
            await session.commit()

        a += 1

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(fetch_and_store_messages(chat_id=-1002683131111))