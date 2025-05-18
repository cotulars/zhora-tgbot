from sqlalchemy import Column, String, BigInteger

from src.database.database import Base


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(BigInteger, primary_key=True)
    type = Column(String)
    title = Column(String)


