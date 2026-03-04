from sqlalchemy import select, update
from datetime import datetime

from app.infrastructure.db.models import Session
from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.interfaces.session_repository import (
    ISessionRepository,
)


class SessionRepository(BaseRepository[Session], ISessionRepository):

    def __init__(self, session):
        super().__init__(session, Session)

    async def get(self, id):
        return await self.get_by_id(id)

    async def active(self):
        q = select(Session).where(Session.logout_time.is_(None))
        r = await self.session.execute(q)
        return r.scalars().all()

    async def by_user(self, user_id):
        return await self.filter(user_id=user_id)

    async def create(self, s):
        return await self.add(s)

    async def end(self, session_id, reason):
        q = (
            update(Session)
            .where(Session.id == session_id)
            .values(logout_time=datetime.utcnow(), end_reason=reason)
        )
        r = await self.session.execute(q)
        await self.session.flush()
        return r.rowcount > 0
