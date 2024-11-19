from typing import Sequence
from datetime import datetime

from sqlalchemy import select, or_, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import DatabaseEngine
from db.models import Eating


class EatingRepository:
    def __init__(self):
        self.session_maker = DatabaseEngine().create_session()

    async def add_eating(self, user_id: int, day_id: int, calories: float, protein: float, fats: float, carbs: float):
        """
        day_id = Column(BigInteger, ForeignKey('days.id'), nullable=False)
        user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
        user: Mapped[Users] = relationship("Users", backref=__tablename__, cascade='all', lazy='subquery')
        calories = Column(BigInteger, nullable=False, unique=False)
        protein = Column(BigInteger, nullable=False, unique=False)
        fats = Column(BigInteger, nullable=False, unique=False)
        carbs = Column(BigInteger, nullable=False, unique=False)
        """
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                eating = Eating(user_id=user_id, day_id=day_id, calories=calories, protein=protein,
                                fats=fats, carbs=carbs)
                try:
                    session.add(eating)
                    await session.flush()
                    eating_id = eating.id
                except Exception:
                    return False
                return eating_id

    async def get_eating_by_eating_id(self, eating_id: int) -> Eating:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(Eating).where(or_(Eating.id == eating_id))
                query = await session.execute(sql)
                return query.scalars().one_or_none()

    async def get_all_eating_by_user_id(self, user_id: int) -> Sequence[Eating]:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(Eating).where(or_(Eating.user_id == user_id))
                query = await session.execute(sql)
                return query.scalars().all()

    async def get_day_eating_by_day_id(self, user_id: int, day_id: int) -> Sequence[Eating]:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(Eating).where(or_(Eating.day_id == day_id))
                query = await session.execute(sql)
                return query.scalars().all()

    async def delete_eating_by_id(self, eating_id: int):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = delete(Eating).where(or_(Eating.id == eating_id))
                await session.execute(sql)
                await session.commit()