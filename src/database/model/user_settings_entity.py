
from sqlalchemy import Column, String, BigInteger, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from src.database.database import Base


class UserSettingsDbEntity(Base):
    __tablename__ = 'users_settings'
    id = Column(BigInteger, primary_key=True)
    settings = Column(JSONB)