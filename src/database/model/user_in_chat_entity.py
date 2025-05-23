from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, BigInteger
from sqlalchemy.sql.sqltypes import Boolean

from src.database.database import Base


class UserInChat(Base):
    __tablename__ = 'users_in_chats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    chat_id = Column(BigInteger, ForeignKey('chats.id'))