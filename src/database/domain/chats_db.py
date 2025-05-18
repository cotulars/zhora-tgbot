from src.database.database import async_session
from src.database.model.chat_entity import Chat


class ChatsDB:

    @staticmethod
    async def add_chat(chat: 'Chat'):
        async with async_session() as session:
            session.add(chat)
            await session.commit()