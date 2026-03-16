from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import with_polymorphic

from app.infrastructure.db.models import (
    DashboardUser,
    Admin as DBAdmin,
    Manager as DBManager,
    DashboardRole as DBRole,
)
from app.domain.entities.entities import (
    DashboardUserEntity,
    DashboardRole,
    AdminEntity,
    ManagerEntity,
)


def _to_entity(o: DashboardUser) -> DashboardUserEntity:
    if isinstance(o, DBAdmin):
        return AdminEntity(
            id=o.id,
            username=o.username,
            hashed_password=o.hashed_password,
            role=DashboardRole.ADMIN,
            created_at=o.created_at,
        )
    elif isinstance(o, DBManager):
        return ManagerEntity(
            id=o.id,
            username=o.username,
            hashed_password=o.hashed_password,
            role=DashboardRole.MANAGER,
            department_id=o.department_id,
            created_at=o.created_at,
        )
    return DashboardUserEntity(
        id=o.id,
        username=o.username,
        hashed_password=o.hashed_password,
        role=DashboardRole(o.role.value),
        created_at=o.created_at,
    )


_poly = with_polymorphic(DashboardUser, [DBAdmin, DBManager])


class DashboardUserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> Optional[DashboardUserEntity]:
        r = await self.db.execute(
            select(_poly).where(DashboardUser.username == username)
        )
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None

    async def get_by_id(self, user_id: int) -> Optional[DashboardUserEntity]:
        r = await self.db.execute(select(_poly).where(DashboardUser.id == user_id))
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None
