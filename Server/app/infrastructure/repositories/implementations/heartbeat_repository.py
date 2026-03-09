# app/infrastructure/repositories/implementations/heartbeat_repository.py
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models import DeviceHeartbeat, Session
from app.infrastructure.repositories.base_repository import BaseRepository


class HeartbeatRepository(BaseRepository[DeviceHeartbeat]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DeviceHeartbeat)

    async def create_heartbeat(
        self, session_id: UUID, device_id: int, user_id: int
    ) -> DeviceHeartbeat:
        heartbeat = DeviceHeartbeat(
            session_id=session_id,
            device_id=device_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
        )
        self.db.add(heartbeat)
        await self.db.commit()
        await self.db.refresh(heartbeat)
        return heartbeat

    async def get_last_heartbeat(self, session_id: UUID) -> Optional[DeviceHeartbeat]:
        query = (
            select(DeviceHeartbeat)
            .where(DeviceHeartbeat.session_id == session_id)
            .order_by(desc(DeviceHeartbeat.timestamp))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_heartbeats_by_session(
        self, session_id: UUID, limit: int = 100
    ) -> List[DeviceHeartbeat]:
        query = (
            select(DeviceHeartbeat)
            .where(DeviceHeartbeat.session_id == session_id)
            .order_by(desc(DeviceHeartbeat.timestamp))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_sessions_without_heartbeat(self, minutes: int = 2) -> List[UUID]:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        active_sessions_query = select(Session.id).where(Session.logout_time.is_(None))
        active_sessions = await self.db.execute(active_sessions_query)
        active_session_ids = [row[0] for row in active_sessions.all()]

        if not active_session_ids:
            return []

        recent_heartbeats_query = (
            select(DeviceHeartbeat.session_id)
            .where(
                and_(
                    DeviceHeartbeat.session_id.in_(active_session_ids),
                    DeviceHeartbeat.timestamp >= cutoff,
                )
            )
            .distinct()
        )
        recent = await self.db.execute(recent_heartbeats_query)
        recent_session_ids = set(row[0] for row in recent.all())

        return [sid for sid in active_session_ids if sid not in recent_session_ids]

    async def cleanup_old_heartbeats(self, days: int = 7):
        cutoff = datetime.utcnow() - timedelta(days=days)

        query = select(DeviceHeartbeat).where(DeviceHeartbeat.timestamp < cutoff)
        result = await self.db.execute(query)
        old_heartbeats = result.scalars().all()

        for hb in old_heartbeats:
            await self.db.delete(hb)

        await self.db.commit()
        return len(old_heartbeats)
