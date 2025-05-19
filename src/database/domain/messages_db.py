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
            last_messages_cte = (
                select(Message)
                .filter_by(chat_id=chat_id)
                .order_by(Message.date.desc())
                .limit(count)
                .cte("last_messages")
            )

            query = (
                select(Message)
                .join(last_messages_cte, Message.id == last_messages_cte.c.id)
                .order_by(last_messages_cte.c.date.asc())
            )
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_messages_from_msg_id_to_latest(chat_id: int, msg_id: int) -> List[Message]:
        async with async_session() as session:
            query = (
                select(Message)
                .filter(
                    Message.chat_id == chat_id,
                    Message.msg_id >= msg_id
                )
                .order_by(Message.msg_id.asc())
            )
            result = await session.execute(query)
            return result.scalars().all()