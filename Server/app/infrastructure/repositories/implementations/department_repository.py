from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.db.models import Department
from app.domain.entities.entities import DepartmentEntity


def _to_entity(db_obj: Department) -> DepartmentEntity:
    return DepartmentEntity(id=db_obj.id, name=db_obj.name)


class DepartmentRepository(BaseRepository[DepartmentEntity]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entity_id: int) -> Optional[DepartmentEntity]:
        result = await self.db.execute(
            select(Department).where(Department.id == entity_id)
        )
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_by_name(self, name: str) -> Optional[DepartmentEntity]:
        result = await self.db.execute(
            select(Department).where(Department.name == name)
        )
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_all(self) -> List[DepartmentEntity]:
        result = await self.db.execute(select(Department))
        return [_to_entity(r) for r in result.scalars().all()]

    async def create(self, entity: DepartmentEntity) -> DepartmentEntity:
        db_obj = Department(id=entity.id, name=entity.name)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def update(self, entity: DepartmentEntity) -> DepartmentEntity:
        result = await self.db.execute(
            select(Department).where(Department.id == entity.id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise ValueError(f"Department {entity.id} not found")
        db_obj.name = entity.name
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def delete(self, entity_id: int) -> bool:
        result = await self.db.execute(
            select(Department).where(Department.id == entity_id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
