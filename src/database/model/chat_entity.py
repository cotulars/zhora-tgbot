from sqlalchemy import Column, String, BigInteger
from sqlalchemy.sql.sqltypes import Integer, Boolean

from src.database.database import Base


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(BigInteger, primary_key=True)
    type = Column(String)
    title = Column(String)
    members_count = Column(Integer)
    level = Column(Integer)
    isPrivate = Column(Boolean, default=False)




