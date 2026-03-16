from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.db.models import Alert
from app.domain.entities.entities import AlertEntity, AlertType


def _to_entity(db_obj: Alert) -> AlertEntity:
    return AlertEntity(
        id=db_obj.id,
        type=AlertType(db_obj.type.value),
        session_id=db_obj.session_id,
        employee_id=db_obj.employee_id,
        created_at=db_obj.created_at,
    )


class AlertRepository(BaseRepository[AlertEntity]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entity_id: int) -> Optional[AlertEntity]:
        result = await self.db.execute(select(Alert).where(Alert.id == entity_id))
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_by_session(self, session_id: UUID) -> List[AlertEntity]:
        result = await self.db.execute(
            select(Alert).where(Alert.session_id == session_id)
        )
        return [_to_entity(r) for r in result.scalars().all()]

    async def get_by_employee(self, employee_id: int) -> List[AlertEntity]:
        result = await self.db.execute(
            select(Alert).where(Alert.employee_id == employee_id)
        )
        return [_to_entity(r) for r in result.scalars().all()]

    async def get_all(self) -> List[AlertEntity]:
        result = await self.db.execute(select(Alert))
        return [_to_entity(r) for r in result.scalars().all()]

    async def create(self, entity: AlertEntity) -> AlertEntity:
        from app.infrastructure.db.models import AlertType as DBAlertType

        db_obj = Alert(
            id=entity.id,
            type=DBAlertType(entity.type.value),
            session_id=entity.session_id,
            employee_id=entity.employee_id,
            created_at=entity.created_at,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def update(self, entity: AlertEntity) -> AlertEntity:
        raise NotImplementedError("Alerts are immutable.")

    async def delete(self, entity_id: int) -> bool:
        result = await self.db.execute(select(Alert).where(Alert.id == entity_id))
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
