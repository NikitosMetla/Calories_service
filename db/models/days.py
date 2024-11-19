from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Boolean, Float
from sqlalchemy.orm import Mapped, relationship

from db.base import BaseModel, CleanModel
from .users import Users


class Days(BaseModel, CleanModel):

    __tablename__ = 'days'

    number_day = Column(BigInteger, unique=False, nullable=False)
    total_calories = Column(Float, nullable=False, unique=False, default=0)
    total_protein = Column(Float, nullable=False, unique=False, default=0)
    total_fats = Column(Float, nullable=False, unique=False, default=0)
    total_carbs = Column(Float, nullable=False, unique=False, default=0)
    # send_notification = Column(Boolean, nullable=False, default=False)
    send_free_message = Column(Boolean, nullable=False, default=False, unique=False)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    user: Mapped[Users] = relationship("Users", backref=__tablename__, cascade='all', lazy='subquery')

    @property
    def stats(self) -> str:
        """
        :return:
        """
        return ""

    def __str__(self) -> str:
        return f"<{self.__tablename__}:{self.id}>"

    def __repr__(self):
        return self.__str__()