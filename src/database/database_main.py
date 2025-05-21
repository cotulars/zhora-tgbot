from src.app import bot
from src.database.database import engine, Base
from src.database.domain.users_db import UsersDB
from src.database.model.user_entity import User


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if not await UsersDB.is_user_exists(bot.id):
        udb = UsersDB()
        await udb.add_user(
            User(
                id=bot.id,
                username="zhora_superbot",
                name="Жора",
                is_activated=True
            )
        )
        await udb.close()