from typing import Any, Coroutine, Sequence

import sqlalchemy
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.database.database import async_session
from src.database.model.chat_entity import Chat


class ChatsDB:

    @staticmethod
    async def add_chat(chat: 'Chat'):
        async with async_session() as session:
            session.add(chat)
            await session.commit()

    @staticmethod
    async def get_all_chats() -> Sequence[Chat]:
        session: AsyncSession
        async with async_session() as session:
            result = await session.execute(
                sqlalchemy.select(Chat)
            )

            return result.scalars().all()