from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.db.models import DeviceHeartbeat
from app.domain.entities.entities import HeartbeatEntity


def _to_entity(db_obj: DeviceHeartbeat) -> HeartbeatEntity:
    return HeartbeatEntity(
        id=db_obj.id,
        session_id=db_obj.session_id,
        employee_id=db_obj.employee_id,
        timestamp=db_obj.timestamp,
    )


class HeartbeatRepository(BaseRepository[HeartbeatEntity]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entity_id: int) -> Optional[HeartbeatEntity]:
        result = await self.db.execute(
            select(DeviceHeartbeat).where(DeviceHeartbeat.id == entity_id)
        )
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_by_session(self, session_id: UUID) -> List[HeartbeatEntity]:
        result = await self.db.execute(
            select(DeviceHeartbeat).where(DeviceHeartbeat.session_id == session_id)
        )
        return [_to_entity(r) for r in result.scalars().all()]

    async def get_latest_by_session(
        self, session_id: UUID
    ) -> Optional[HeartbeatEntity]:
        result = await self.db.execute(
            select(DeviceHeartbeat)
            .where(DeviceHeartbeat.session_id == session_id)
            .order_by(DeviceHeartbeat.timestamp.desc())
            .limit(1)
        )
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_all(self) -> List[HeartbeatEntity]:
        result = await self.db.execute(select(DeviceHeartbeat))
        return [_to_entity(r) for r in result.scalars().all()]

    async def create(self, entity: HeartbeatEntity) -> HeartbeatEntity:
        db_obj = DeviceHeartbeat(
            id=entity.id,
            session_id=entity.session_id,
            employee_id=entity.employee_id,
            timestamp=entity.timestamp,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def update(self, entity: HeartbeatEntity) -> HeartbeatEntity:
        # Heartbeats are immutable; nothing to update
        raise NotImplementedError("Heartbeats are append-only.")

    async def delete(self, entity_id: int) -> bool:
        result = await self.db.execute(
            select(DeviceHeartbeat).where(DeviceHeartbeat.id == entity_id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
