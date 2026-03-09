from sqlalchemy import select, update, desc
from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict, Any

from app.infrastructure.db.models import Session as SessionModel
from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.interfaces.session_repository import (
    ISessionRepository,
)


class SessionRepository(BaseRepository[SessionModel], ISessionRepository):

    def __init__(self, session):
        super().__init__(session, SessionModel)

    async def get(self, id: UUID) -> Optional[SessionModel]:
        return await self.get_by_id(id)

    async def list(self, skip: int = 0, limit: int = 100) -> List[SessionModel]:
        query = (
            select(self.model_class)
            .order_by(desc(self.model_class.login_time))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def active(self) -> List[SessionModel]:
        query = select(self.model_class).where(self.model_class.logout_time.is_(None))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_active(self) -> List[SessionModel]:
        return await self.active()

    async def by_user(self, user_id: int) -> List[SessionModel]:
        return await self.filter(user_id=user_id)

    async def get_user_sessions(
        self, user_id: int, active_only: bool = False
    ) -> List[SessionModel]:
        query = select(self.model_class).where(self.model_class.user_id == user_id)

        if active_only:
            query = query.where(self.model_class.logout_time.is_(None))

        query = query.order_by(desc(self.model_class.login_time))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def by_device(self, device_id: int) -> List[SessionModel]:
        return await self.filter(device_id=device_id)

    async def get_device_sessions(
        self, device_id: int, active_only: bool = False
    ) -> List[SessionModel]:
        query = select(self.model_class).where(self.model_class.device_id == device_id)

        if active_only:
            query = query.where(self.model_class.logout_time.is_(None))

        query = query.order_by(desc(self.model_class.login_time))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_active_sessions(
        self, device_id: Optional[int] = None, user_id: Optional[int] = None
    ) -> List[SessionModel]:
        query = select(self.model_class).where(self.model_class.logout_time.is_(None))

        if device_id:
            query = query.where(self.model_class.device_id == device_id)
        if user_id:
            query = query.where(self.model_class.user_id == user_id)

        query = query.order_by(desc(self.model_class.login_time))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, s: SessionModel) -> SessionModel:
        return await self.add(s)

    async def end(self, session_id: UUID, reason: str) -> bool:
        query = (
            update(self.model_class)
            .where(self.model_class.id == session_id)
            .where(self.model_class.logout_time.is_(None))
            .values(logout_time=datetime.utcnow(), end_reason=reason)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def get_stats(self) -> Dict[str, Any]:
        from sqlalchemy import func

        total_query = select(func.count()).select_from(self.model_class)
        total_result = await self.session.execute(total_query)
        total = total_result.scalar()

        active_query = select(func.count()).where(
            self.model_class.logout_time.is_(None)
        )
        active_result = await self.session.execute(active_query)
        active = active_result.scalar()

        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_query = select(func.count()).where(
            self.model_class.login_time >= today_start
        )
        today_result = await self.session.execute(today_query)
        today = today_result.scalar()

        return {
            "total_sessions": total or 0,
            "active_sessions": active or 0,
            "today_sessions": today or 0,
        }
