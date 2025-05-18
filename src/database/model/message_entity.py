from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, BigInteger

from src.database.database import Base

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    msg_id = Column(BigInteger)
    chat_id = Column(BigInteger, ForeignKey('chats.id'))
    user_id = Column(BigInteger, ForeignKey('users.id'))
    text = Column(String, nullable=True)
    media_content = Column(String, nullable=True)
    reply_to_msg_id = Column(BigInteger, nullable=True)
    date = Column(DateTime)