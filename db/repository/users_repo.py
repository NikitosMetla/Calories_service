from datetime import datetime
from typing import Sequence

from sqlalchemy import select, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import DatabaseEngine
from db.models import Users


class UserRepository:
    def __init__(self):
        self.session_maker = DatabaseEngine().create_session()

    async def add_user(self, user_id: int, username: str):
        """user_id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
            username = Column(String, nullable=True, unique=False)
            donate = Column(Boolean, default=False, unique=False)
            activate_trial_period = Column(Boolean, default=True, unique=False)
            end_trial_period = Column(Boolean, default=False, unique=False)
            notification = Column(Boolean, default=True, unique=False)
            notification_time = Column(Time, nullable=True, unique=False, default=time(23, 0))
            day_now_id = Column(BigInteger, ForeignKey("days.id"), nullable=True)"""
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                user = Users(user_id=user_id, username=username)
                try:
                    session.add(user)
                except Exception:
                    return False
                return True

    async def get_user_by_user_id(self, user_id: int) -> Users:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(Users).where(or_(Users.user_id == user_id))
                query = await session.execute(sql)
                return query.scalars().one_or_none()

    async def select_all_users(self) -> Sequence[Users]:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(Users)
                query = await session.execute(sql)
                return query.scalars().all()

    async def update_donate_by_user_id(self, user_id: int):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Users).values({
                    Users.donate: True
                }).where(or_(Users.user_id == user_id))
                await session.execute(sql)
                await session.commit()

    async def update_time_notification_by_user_id(self, user_id: int, time_notification: str):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Users).values({
                    Users.notification_time: time_notification
                }).where(or_(Users.user_id == user_id))
                await session.execute(sql)
                await session.commit()

    async def update_email_by_user_id(self, user_id: int, email: str):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Users).values({
                    Users.email: email
                }).where(or_(Users.user_id == user_id))
                await session.execute(sql)
                await session.commit()

    async def update_day_by_user_id(self, user_id: int, day: int):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Users).values({
                    Users.day_now: day
                }).where(or_(Users.user_id == user_id))
                await session.execute(sql)
                await session.commit()

    async def update_thread_id_by_user_id(self, user_id: int, thread_id: int):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Users).values({
                    Users.ai_threat_id: thread_id
                }).where(or_(Users.user_id == user_id))
                await session.execute(sql)
                await session.commit()

    async def deactivate_notification_by_user_id(self, user_id: int):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Users).values({
                    Users.notification: False
                }).where(or_(Users.user_id == user_id))
                await session.execute(sql)
                await session.commit()

    async def activate_notification_by_user_id(self, user_id: int):
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = update(Users).values({
                    Users.notification: True
                }).where(or_(Users.user_id == user_id))
                await session.execute(sql)
                await session.commit()



