import sqlalchemy

from src.database.database import async_session
from src.database.model.bot_settings_entity import Setting


class BotSettingsDB:

    settings = {}

    @staticmethod
    async def load_settings():
        async with async_session() as session:
            result = await session.execute(
                sqlalchemy.select(Setting)
            )

            for row in result.scalars():
                BotSettingsDB.settings[row.id] = row.value

    @staticmethod
    async def get_setting(id: str):
        if id in BotSettingsDB.settings:
            return BotSettingsDB.settings[id]
        else:
            return None

    @staticmethod
    async def set_setting(id: str, value: str):
        BotSettingsDB.settings[id] = value
        await BotSettingsDB.save_settings()

    @staticmethod
    async def save_settings():
        async with async_session() as session:
            for id, value in BotSettingsDB.settings.items():
                session.add(Setting(id=id, value=value))
            await session.commit()