from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.db.models import FaceEmbedding
from app.domain.entities.entities import FaceEmbeddingEntity


def _to_entity(db_obj: FaceEmbedding) -> FaceEmbeddingEntity:
    return FaceEmbeddingEntity(
        id=db_obj.id,
        employee_id=db_obj.employee_id,
        embedding=list(db_obj.embedding),
        created_at=db_obj.created_at,
    )


class FaceEmbeddingRepository(BaseRepository[FaceEmbeddingEntity]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entity_id: int) -> Optional[FaceEmbeddingEntity]:
        result = await self.db.execute(
            select(FaceEmbedding).where(FaceEmbedding.id == entity_id)
        )
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_by_employee_id(
        self, employee_id: int
    ) -> Optional[FaceEmbeddingEntity]:
        result = await self.db.execute(
            select(FaceEmbedding).where(FaceEmbedding.employee_id == employee_id)
        )
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_by_username(self, username: str) -> Optional[FaceEmbeddingEntity]:
        """Lookup embedding via Employee.username JOIN."""
        from app.infrastructure.db.models import Employee

        result = await self.db.execute(
            select(FaceEmbedding)
            .join(Employee, Employee.id == FaceEmbedding.employee_id)
            .where(Employee.username == username)
        )
        obj = result.scalar_one_or_none()
        return _to_entity(obj) if obj else None

    async def get_all(self) -> List[FaceEmbeddingEntity]:
        result = await self.db.execute(select(FaceEmbedding))
        return [_to_entity(r) for r in result.scalars().all()]

    async def create(self, entity: FaceEmbeddingEntity) -> FaceEmbeddingEntity:
        db_obj = FaceEmbedding(
            id=entity.id,
            employee_id=entity.employee_id,
            embedding=entity.embedding,
            created_at=entity.created_at,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def update(self, entity: FaceEmbeddingEntity) -> FaceEmbeddingEntity:
        result = await self.db.execute(
            select(FaceEmbedding).where(FaceEmbedding.id == entity.id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise ValueError(f"FaceEmbedding {entity.id} not found")
        db_obj.embedding = entity.embedding
        await self.db.commit()
        await self.db.refresh(db_obj)
        return _to_entity(db_obj)

    async def delete(self, entity_id: int) -> bool:
        result = await self.db.execute(
            select(FaceEmbedding).where(FaceEmbedding.id == entity_id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
