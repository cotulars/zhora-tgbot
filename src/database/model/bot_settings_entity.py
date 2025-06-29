from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String

from src.database.database import Base


class Setting(Base):
    __tablename__ = 'bot_settings'
    id = Column(String, primary_key=True)
    value = Column(String)