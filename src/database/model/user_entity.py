
from sqlalchemy import Column, String, BigInteger, Boolean

from src.database.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    name = Column(String)
    is_activated = Column(Boolean, default=False)
