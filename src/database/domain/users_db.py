import json
from typing import Optional

import sqlalchemy
from sqlalchemy.orm import class_mapper

from src.app import redis_client
from src.database.database import async_session
from src.database.domain.settings_db import SettingsDB
from src.database.model.user_entity import User

def user_to_dict(obj: 'User'):
    return {
        "id": obj.id,
        "username": obj.username,
        "name": obj.name,
        "is_activated": obj.is_activated
    }

def dict_to_user(data: dict) -> User:
    return User(
        id=data["id"],
        username=data["username"],
        name=data["name"],
        is_activated=data["is_activated"]
    )


class UsersDB:
    USER_TTL = 60 * 60

    def __init__(self):
        self.session = async_session()

    async def add_user(self, user: 'User'):
        self.session.add(user)
        await self.session.commit()
        await SettingsDB.init_settings_for_user(user.id)

    async def get_user(self, user_id: int, no_cache = False) -> Optional['User']:
        if not no_cache:
            if redis_client.exists(f"user:{user_id}"):
                return dict_to_user(json.loads(redis_client.get(f"user:{user_id}")))

        result = await self.session.execute(
            sqlalchemy.select(User)
                .filter_by(id=user_id)
        )
        response = result.scalar_one_or_none()
        if response:
            redis_client.set(f"user:{user_id}", json.dumps(user_to_dict(response)), ex=UsersDB.USER_TTL)
        return response

    @staticmethod
    async def is_user_exists(user_id: int) -> bool:
        if redis_client.exists(f"user:{user_id}"): return True
        else:
            db = UsersDB()
            if await db.get_user(user_id):
                await db.close()
                return True
            else:
                await db.close()
                return False

    async def commit(self):
        await self.session.commit()

    async def close(self):
        await self.session.close()