from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from app.infrastructure.db.models import FaceEmbedding
from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.interfaces.embedding_repository import (
    IFaceEmbeddingRepository,
)


class FaceEmbeddingRepository(BaseRepository[FaceEmbedding], IFaceEmbeddingRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, FaceEmbedding)

    async def get_by_id(self, id: int) -> Optional[FaceEmbedding]:
        return await self.get_by_id(id)

    async def get_by_user(self, user_id: int) -> List[FaceEmbedding]:
        return await self.filter(user_id=user_id)

    async def get_by_user_ids(self, user_ids: List[int]) -> List[FaceEmbedding]:
        if not user_ids:
            return []

        query = select(self.model_class).where(self.model_class.user_id.in_(user_ids))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, embedding: FaceEmbedding) -> FaceEmbedding:
        return await self.add(embedding)

    async def update(self, embedding: FaceEmbedding) -> FaceEmbedding:
        return await super().update(embedding)

    async def delete(self, embedding_id: int) -> bool:
        return await self.delete_by_id(embedding_id)

    async def list_all(self) -> List[FaceEmbedding]:
        return await self.get_all()

    async def delete_by_user(self, user_id: int) -> bool:
        try:
            query = delete(self.model_class).where(self.model_class.user_id == user_id)
            result = await self.session.execute(query)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            raise e
