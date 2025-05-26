import dataclasses
from dataclasses import dataclass, field

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.database import async_session
from src.database.model.chat_entity import Chat
from src.database.model.user_settings_entity import UserSettingsDbEntity


@dataclass
class NotificationsSettings:
    enabled: bool = True

@dataclass
class ChatSettings:
    reply_to_mentions: bool = True
    inactive_summary: bool = True
    inactive_summary_interval: int = 240 # in minutes


@dataclass
class UserSettings:
    notifications: NotificationsSettings = field(default_factory=NotificationsSettings)
    chats: dict[int, ChatSettings] = field(default_factory=dict)
    timezone: int = 3
    lang: str = 'en'

class SettingsDB:

    @staticmethod
    async def init_settings_for_user(user_id: int):
        async with async_session() as session:
            session.add(UserSettingsDbEntity(
                id=user_id,
                settings=dataclasses.asdict(UserSettings())
            ))
            await session.commit()

    @staticmethod
    async def update_settings(user_id: int, settings: UserSettings):
        session: AsyncSession
        async with async_session() as session:
            result = await session.execute(
                sqlalchemy.select(UserSettingsDbEntity)
                    .filter_by(id=user_id)
            )
            response = result.scalar_one_or_none()

            if not response:
                await SettingsDB.init_settings_for_user(user_id)
                return
            else:
                response.settings = dataclasses.asdict(settings)
                await session.commit()

    @staticmethod
    async def get_settings(user_id: int) -> 'UserSettings':
        session: AsyncSession
        async with async_session() as session:
            result = await session.execute(
                sqlalchemy.select(UserSettingsDbEntity)
                    .filter_by(id=user_id)
            )
            response = result.scalar_one_or_none()

            if response:
                return UserSettings(**response.settings)
            return UserSettings()
