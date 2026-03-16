from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.db.models import Employee
from app.domain.entities.entities import EmployeeEntity


def _to_entity(db_obj: Employee) -> EmployeeEntity:
    return EmployeeEntity(
        id=db_obj.id,
        name=db_obj.name,
        username=db_obj.username,
        department_id=db_obj.department_id,
        worked_hours=db_obj.worked_hours,
        is_online=db_obj.is_online,
        created_at=db_obj.created_at,
    )


class EmployeeRepository(BaseRepository[EmployeeEntity]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entity_id: int) -> Optional[EmployeeEntity]:
        r = await self.db.execute(select(Employee).where(Employee.id == entity_id))
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None

    async def get_by_username(self, username: str) -> Optional[EmployeeEntity]:
        r = await self.db.execute(select(Employee).where(Employee.username == username))
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None

    async def get_by_department(self, department_id: int) -> List[EmployeeEntity]:
        r = await self.db.execute(
            select(Employee).where(Employee.department_id == department_id)
        )
        return [_to_entity(o) for o in r.scalars().all()]

    async def get_all(self) -> List[EmployeeEntity]:
        r = await self.db.execute(select(Employee))
        return [_to_entity(o) for o in r.scalars().all()]

    async def create(self, entity: EmployeeEntity) -> EmployeeEntity:
        db_obj = Employee(
            name=entity.name,
            username=entity.username,
            department_id=entity.department_id,
            worked_hours=entity.worked_hours,
            is_online=entity.is_online,
            created_at=entity.created_at,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def update(self, entity: EmployeeEntity) -> EmployeeEntity:
        r = await self.db.execute(select(Employee).where(Employee.id == entity.id))
        db_obj = r.scalar_one_or_none()
        if not db_obj:
            raise ValueError(f"Employee {entity.id} not found")
        db_obj.name = entity.name
        db_obj.username = entity.username
        db_obj.department_id = entity.department_id
        db_obj.worked_hours = entity.worked_hours
        db_obj.is_online = entity.is_online
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def delete(self, entity_id: int) -> bool:
        r = await self.db.execute(select(Employee).where(Employee.id == entity_id))
        db_obj = r.scalar_one_or_none()
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
