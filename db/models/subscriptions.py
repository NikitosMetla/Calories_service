from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship

from db.base import BaseModel, CleanModel
from .users import Users


class Subscriptions(BaseModel, CleanModel):
    """
    Таблица юзеров
    """
    __tablename__ = 'subscriptions'

    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    user: Mapped[Users] = relationship("Users", backref=__tablename__, cascade='all', lazy='subquery')
    trial_sub = Column(Boolean, nullable=False, default=False)
    time_limit_subscription = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

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
