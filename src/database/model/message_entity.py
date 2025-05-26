from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, BigInteger
from sqlalchemy.sql.sqltypes import Boolean

from src.database.database import Base

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    msg_id = Column(BigInteger)
    chat_id = Column(BigInteger, ForeignKey('chats.id'))
    user_id = Column(BigInteger, ForeignKey('users.id'))
    text = Column(String, nullable=True)
    media_content_type = Column(String, nullable=True)
    media_content_description = Column(String, nullable=True)
    media_content_id = Column(String, nullable=True)
    reply_to_msg_id = Column(BigInteger, nullable=True)
    quote_from_reply = Column(String, nullable=True)
    is_forwarded = Column(Boolean, default=False)
    forward_from = Column(String, nullable=True)
    is_sticker = Column(Boolean, default=False)
    sticker_description = Column(String, nullable=True)
    is_voice = Column(Boolean, default=False)
    voice_description = Column(String, nullable=True)
    have_url = Column(Boolean, default=False)
    url_content_description = Column(String, nullable=True)
    url_raw = Column(String, nullable=True)
    date = Column(DateTime)