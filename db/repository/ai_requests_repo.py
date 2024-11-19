from typing import Sequence, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import DatabaseEngine
from db.models import AiRequests


class AiRequestsRepository:
    def __init__(self):
        self.session_maker = DatabaseEngine().create_session()

    async def add_request(self,
                          answer_ai: str,
                          user_id: int,
                          has_photo: bool,
                          photo_id: str | None = None
                          ) -> bool:
        """

        user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
        user: Mapped[Users] = relationship("Users", backref=__tablename__, cascade='all', lazy='subquery')
        answer_ai = Column(String, nullable=False)
        has_photo = Column(Boolean, nullable=False, default=False)
        photo_id = Column(String, nullable=False)

        """
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = AiRequests(user_id=user_id, answer_ai=answer_ai, photo_id=photo_id, has_photo=has_photo)
                try:
                    session.add(sql)
                except Exception:
                    return False
                return True

    async def get_request_info_by_id(self, request_id: int) -> Optional[AiRequests]:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(AiRequests).where(or_(AiRequests.id == request_id))
                query = await session.execute(sql)
                return query.scalars().one_or_none()

    async def select_all_requests(self) -> Sequence[AiRequests]:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(AiRequests)
                query = await session.execute(sql)
                return query.scalars().all()

    async def select_all_photo_requests(self) -> Sequence[AiRequests]:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(AiRequests).where(or_(AiRequests.has_photo == True))
                query = await session.execute(sql)
                return query.scalars().all()

    async def get_requests_by_user_id(self, user_id: int) -> Sequence[AiRequests]:
        async with self.session_maker() as session:
            session: AsyncSession
            async with session.begin():
                sql = select(AiRequests).where(or_(AiRequests.user_id == user_id))
                query = await session.execute(sql)
                return query.scalars().all()


