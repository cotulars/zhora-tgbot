from typing import List

from sqlalchemy import select

from src.database.database import async_session
from src.database.model.message_entity import Message


class MessagesDB:

    @staticmethod
    async def add_message(message: 'Message'):
        async with async_session() as session:
            session.add(message)
            await session.commit()

    @staticmethod
    async def get_messages(chat_id, count: int = 30) -> List['Message']:
        async with async_session() as session:
            # 1) CTE: N самых новых сообщений (DESC)
            last_messages_cte = (
                select(Message)
                .filter_by(chat_id=chat_id)
                .order_by(Message.date.desc())
                .limit(count)
                .cte("last_messages")
            )

            # 2) Основной запрос: join с CTE и сортировка по возрастанию даты (ASC)
            query = (
                select(Message)
                .join(last_messages_cte, Message.id == last_messages_cte.c.id)
                .order_by(last_messages_cte.c.date.asc())
            )

            # 3) Выполняем и возвращаем результаты
            result = await session.execute(query)
            return result.scalars().all()