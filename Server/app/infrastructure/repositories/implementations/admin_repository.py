from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.db.models import Admin as DBAdmin
from app.domain.entities.entities import AdminEntity, DashboardRole


def _to_entity(o: DBAdmin) -> AdminEntity:
    return AdminEntity(
        id=o.id,
        username=o.username,
        hashed_password=o.hashed_password,
        role=DashboardRole.ADMIN,
        created_at=o.created_at,
    )


class AdminRepository(BaseRepository[AdminEntity]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entity_id: int) -> Optional[AdminEntity]:
        r = await self.db.execute(select(DBAdmin).where(DBAdmin.id == entity_id))
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None

    async def get_by_username(self, username: str) -> Optional[AdminEntity]:
        r = await self.db.execute(select(DBAdmin).where(DBAdmin.username == username))
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None

    async def get_all(self) -> List[AdminEntity]:
        r = await self.db.execute(select(DBAdmin))
        return [_to_entity(o) for o in r.scalars().all()]

    async def create(self, entity: AdminEntity) -> AdminEntity:
        obj = DBAdmin(
            username=entity.username,
            hashed_password=entity.hashed_password,
            created_at=entity.created_at,
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return _to_entity(obj)

    async def update(self, entity: AdminEntity) -> AdminEntity:
        r = await self.db.execute(select(DBAdmin).where(DBAdmin.id == entity.id))
        obj = r.scalar_one_or_none()
        if not obj:
            raise ValueError(f"Admin {entity.id} not found")
        obj.username = entity.username
        obj.hashed_password = entity.hashed_password
        await self.db.commit()
        await self.db.refresh(obj)
        return _to_entity(obj)

    async def delete(self, entity_id: int) -> bool:
        r = await self.db.execute(select(DBAdmin).where(DBAdmin.id == entity_id))
        obj = r.scalar_one_or_none()
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
