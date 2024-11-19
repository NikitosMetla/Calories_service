from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Float
from sqlalchemy.orm import Mapped, relationship

from db.base import BaseModel, CleanModel
from .users import Users


class Eating(BaseModel, CleanModel):

    __tablename__ = 'eating'

    day_id = Column(BigInteger, ForeignKey('days.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    user: Mapped[Users] = relationship("Users", backref=__tablename__, cascade='all', lazy='subquery')
    calories = Column(Float, nullable=False, unique=False)
    protein = Column(Float, nullable=False, unique=False)
    fats = Column(Float, nullable=False, unique=False)
    carbs = Column(Float, nullable=False, unique=False)

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