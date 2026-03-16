from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.db.models import Session
from app.domain.entities.entities import SessionEntity, SessionEndReason


def _to_entity(db_obj: Session) -> SessionEntity:
    return SessionEntity(
        id=db_obj.id,
        employee_id=db_obj.employee_id,
        login_time=db_obj.login_time,
        logout_time=db_obj.logout_time,
        end_reason=(
            SessionEndReason(db_obj.end_reason.value) if db_obj.end_reason else None
        ),
    )


class SessionRepository(BaseRepository[SessionEntity]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entity_id: UUID) -> Optional[SessionEntity]:
        result = await self.db.execute(select(Session).where(Session.id == entity_id))
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_active_by_employee(self, employee_id: int) -> Optional[SessionEntity]:
        """Returns the currently open session (no logout_time) for an employee."""
        result = await self.db.execute(
            select(Session).where(
                Session.employee_id == employee_id,
                Session.logout_time.is_(None),
            )
        )
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_by_employee(self, employee_id: int) -> List[SessionEntity]:
        result = await self.db.execute(
            select(Session).where(Session.employee_id == employee_id)
        )
        return [_to_entity(r) for r in result.scalars().all()]

    async def get_by_department(self, department_id: int) -> List[SessionEntity]:
        """Returns all sessions for employees in a given department."""
        from app.infrastructure.db.models import Employee

        result = await self.db.execute(
            select(Session)
            .join(Employee, Employee.id == Session.employee_id)
            .where(Employee.department_id == department_id)
        )
        return [_to_entity(r) for r in result.scalars().all()]

    async def get_all(self) -> List[SessionEntity]:
        result = await self.db.execute(select(Session))
        return [_to_entity(r) for r in result.scalars().all()]

    async def create(self, entity: SessionEntity) -> SessionEntity:
        from app.infrastructure.db.models import SessionEndReason as DBSessionEndReason

        db_obj = Session(
            id=entity.id,
            employee_id=entity.employee_id,
            login_time=entity.login_time,
            logout_time=entity.logout_time,
            end_reason=(
                DBSessionEndReason(entity.end_reason.value)
                if entity.end_reason
                else None
            ),
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def update(self, entity: SessionEntity) -> SessionEntity:
        from app.infrastructure.db.models import SessionEndReason as DBSessionEndReason

        result = await self.db.execute(select(Session).where(Session.id == entity.id))
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise ValueError(f"Session {entity.id} not found")
        db_obj.logout_time = entity.logout_time
        db_obj.end_reason = (
            DBSessionEndReason(entity.end_reason.value) if entity.end_reason else None
        )
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.db.execute(select(Session).where(Session.id == entity_id))
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
