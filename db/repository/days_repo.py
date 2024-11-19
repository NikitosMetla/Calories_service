from typing import Sequence
from datetime import datetime

from sqlalchemy import select, or_, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import DatabaseEngine
from db.models import Days


class DaysRepository:
    def __init__(self):
        self.session_maker = DatabaseEngine().create_session()

    async def add_day(self, user_id: int, number_day: int):
        """     number_day = Column(Integer, primary_key=True, unique=False, nullable=False)
                total_calories = Column(Integer, nullable=False, unique=False, default=0)
                user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
                user: Mapped[Users] = relationship("Users", backref=__tablename__, cascade='all', lazy='subquery')
        """
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                day = Days(user_id=user_id, number_day=number_day)
                try:
                    session.add(day)
                except Exception:
                    return False
                return True

    async def update_day_params_by_day_id(self, day_id: int, added_calories: float,
                                          added_protein: float,
                                          added_fats: float,
                                          added_carbs: float):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Days).values({
                    Days.total_calories: Days.total_calories + added_calories,
                    Days.total_protein: Days.total_protein + added_protein,
                    Days.total_fats: Days.total_fats + added_fats,
                    Days.total_carbs: Days.total_carbs + added_carbs
                }).where(or_(Days.id == day_id))
                await session.execute(sql)
                await session.commit()

    async def update_day_calories_by_day_id(self, day_id: int, added_calories: float):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Days).values({
                    Days.total_calories: Days.total_calories + added_calories
                }).where(or_(Days.id == day_id))
                await session.execute(sql)
                await session.commit()

    async def update_day_protein_by_day_id(self, day_id: int, added_protein: float):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Days).values({
                    Days.total_protein: Days.total_protein + added_protein
                }).where(or_(Days.id == day_id))
                await session.execute(sql)
                await session.commit()

    async def update_day_fats_by_day_id(self, day_id: int, added_fats: float):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Days).values({
                    Days.total_protein: Days.total_protein + added_fats
                }).where(or_(Days.id == day_id))
                await session.execute(sql)
                await session.commit()

    async def update_day_carbs_by_day_id(self, day_id: int, addded_carbs: float):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Days).values({
                    Days.total_protein: Days.total_protein + addded_carbs
                }).where(or_(Days.id == day_id))
                await session.execute(sql)
                await session.commit()

    async def update_send_free_message_by_day_id(self, day_id: int):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Days).values({
                    Days.send_free_message: True
                }).where(or_(Days.id == day_id))
                await session.execute(sql)
                await session.commit()
    #
    # async def update_day_notifications_by_day_id(self, day_id: int, added_calories: int):
    #     async with self.session_maker() as session:
    #         session: AsyncSession
    #         async with session.begin():
    #             sql = update(Days).values({
    #                 Days.send_notification: True
    #             }).where(or_(Days.id == day_id))
    #             await session.execute(sql)
    #             await session.commit()

    async def get_day_by_day_id(self, day_id: int) -> Days:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(Days).where(or_(Days.id == day_id))
                query = await session.execute(sql)
                return query.scalars().one_or_none()

    async def get_day_by_number_day_and_user_id(self, user_id: int, day_number: int) -> Days:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(Days).where(and_(Days.user_id == user_id,
                                              Days.number_day == day_number))
                query = await session.execute(sql)
                return query.scalars().one_or_none()

    async def get_days_by_user_id(self, user_id: int) -> Sequence[Days]:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(Days).where(or_(Days.user_id == user_id))
                query = await session.execute(sql)
                return query.scalars().all()