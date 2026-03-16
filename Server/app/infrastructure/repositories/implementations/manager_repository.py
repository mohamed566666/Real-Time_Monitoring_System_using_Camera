from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.db.models import Manager as DBManager
from app.domain.entities.entities import ManagerEntity, DashboardRole


def _to_entity(o: DBManager) -> ManagerEntity:
    return ManagerEntity(
        id=o.id,
        username=o.username,
        hashed_password=o.hashed_password,
        role=DashboardRole.MANAGER,
        department_id=o.department_id,
        created_at=o.created_at,
    )


class ManagerRepository(BaseRepository[ManagerEntity]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entity_id: int) -> Optional[ManagerEntity]:
        r = await self.db.execute(select(DBManager).where(DBManager.id == entity_id))
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None

    async def get_by_username(self, username: str) -> Optional[ManagerEntity]:
        r = await self.db.execute(
            select(DBManager).where(DBManager.username == username)
        )
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None

    async def get_all(self) -> List[ManagerEntity]:
        r = await self.db.execute(select(DBManager))
        return [_to_entity(o) for o in r.scalars().all()]

    async def create(self, entity: ManagerEntity) -> ManagerEntity:
        obj = DBManager(
            username=entity.username,
            hashed_password=entity.hashed_password,
            department_id=entity.department_id,
            created_at=entity.created_at,
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return _to_entity(obj)

    async def update(self, entity: ManagerEntity) -> ManagerEntity:
        r = await self.db.execute(select(DBManager).where(DBManager.id == entity.id))
        obj = r.scalar_one_or_none()
        if not obj:
            raise ValueError(f"Manager {entity.id} not found")
        obj.username = entity.username
        obj.hashed_password = entity.hashed_password
        obj.department_id = entity.department_id
        await self.db.commit()
        await self.db.refresh(obj)
        return _to_entity(obj)

    async def delete(self, entity_id: int) -> bool:
        r = await self.db.execute(select(DBManager).where(DBManager.id == entity_id))
        obj = r.scalar_one_or_none()
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True

    async def get_by_department(self, department_id: int) -> Optional[ManagerEntity]:
        r = await self.db.execute(
            select(DBManager).where(DBManager.department_id == department_id)
        )
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None
