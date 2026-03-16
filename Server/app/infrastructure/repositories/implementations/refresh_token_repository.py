from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.db.models import RefreshToken
from app.domain.entities.entities import RefreshTokenEntity


def _to_entity(o: RefreshToken) -> RefreshTokenEntity:
    return RefreshTokenEntity(
        id=o.id,
        user_id=o.user_id,
        token_hash=o.token_hash,
        expires_at=o.expires_at,
        created_at=o.created_at,
    )


class RefreshTokenRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshTokenEntity]:
        r = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        o = r.scalar_one_or_none()
        return _to_entity(o) if o else None

    async def get_all_by_user(self, user_id: int) -> List[RefreshTokenEntity]:
        r = await self.db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return [_to_entity(o) for o in r.scalars().all()]

    async def create(self, entity: RefreshTokenEntity) -> RefreshTokenEntity:
        obj = RefreshToken(
            user_id=entity.user_id,
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return _to_entity(obj)

    async def delete_by_token_hash(self, token_hash: str) -> bool:
        r = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        obj = r.scalar_one_or_none()
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True

    async def delete_all_by_user(self, user_id: int) -> None:
        """Logout from all devices."""
        r = await self.db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        for obj in r.scalars().all():
            await self.db.delete(obj)
        await self.db.commit()

    async def delete_expired(self) -> None:
        """Cleanup — call periodically."""
        r = await self.db.execute(
            select(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
        )
        for obj in r.scalars().all():
            await self.db.delete(obj)
        await self.db.commit()
