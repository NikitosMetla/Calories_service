from datetime import time
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, ForeignKey, Time

from db.base import BaseModel, CleanModel


class Users(BaseModel, CleanModel):
    """
    Таблица юзеров
    """
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    username = Column(String, nullable=True, unique=False)
    donate = Column(Boolean, default=False, unique=False)
    notification = Column(Boolean, default=True, unique=False)
    notification_time = Column(String, nullable=True, unique=False, default="23:00")
    day_now = Column(BigInteger, unique=False, nullable=True, default=1)
    email = Column(String, nullable=True, unique=False)
    ai_threat_id = Column(String, nullable=True, unique=True)


    @property
    def stats(self) -> str:
        """
        :return:
        """
        return ""

    def __str__(self) -> str:
        return f"<{self.__tablename__}:{self.user_id}>"

    def __repr__(self):
        return self.__str__()
