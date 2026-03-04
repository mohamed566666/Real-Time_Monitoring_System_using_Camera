from typing import List, Optional
from app.infrastructure.repositories.implementations.face_embedding_repository import (
    FaceEmbeddingRepository,
)
from app.domain.entities.face_embedding import FaceEmbedding as FaceEmbeddingEntity
from app.infrastructure.db.models import FaceEmbedding as FaceEmbeddingModel


class FaceEmbeddingService:
    def __init__(self, embedding_repo: FaceEmbeddingRepository):
        self.embedding_repo = embedding_repo

    async def get_embedding(self, embedding_id: int) -> Optional[FaceEmbeddingEntity]:
        """Get embedding by ID"""
        model = await self.embedding_repo.get_by_id(embedding_id)
        if not model:
            return None
        return FaceEmbeddingEntity(
            id=model.id, user_id=model.user_id, embedding=model.embedding
        )

    async def get_embeddings_by_user(self, user_id: int) -> List[FaceEmbeddingEntity]:
        """Get all embeddings for a user"""
        models = await self.embedding_repo.get_by_user(user_id)
        return [
            FaceEmbeddingEntity(id=m.id, user_id=m.user_id, embedding=m.embedding)
            for m in models
        ]

    async def get_embeddings_by_user_ids(
        self, user_ids: List[int]
    ) -> List[FaceEmbeddingEntity]:
        """Get embeddings for multiple users"""
        models = await self.embedding_repo.get_by_user_ids(user_ids)
        return [
            FaceEmbeddingEntity(id=m.id, user_id=m.user_id, embedding=m.embedding)
            for m in models
        ]

    async def list_all_embeddings(self) -> List[FaceEmbeddingEntity]:
        """List all embeddings"""
        models = await self.embedding_repo.list_all()
        return [
            FaceEmbeddingEntity(id=m.id, user_id=m.user_id, embedding=m.embedding)
            for m in models
        ]

    async def create_embedding(
        self, user_id: int, embedding: List[float]
    ) -> FaceEmbeddingEntity:
        """Create new embedding for a user"""
        model = FaceEmbeddingModel(user_id=user_id, embedding=embedding)
        created = await self.embedding_repo.create(model)
        return FaceEmbeddingEntity(
            id=created.id, user_id=created.user_id, embedding=created.embedding
        )

    async def create_embeddings_bulk(
        self, user_id: int, embeddings: List[List[float]]
    ) -> List[FaceEmbeddingEntity]:
        """Create multiple embeddings for a user"""
        models = [
            FaceEmbeddingModel(user_id=user_id, embedding=emb) for emb in embeddings
        ]
        created_list = []
        for model in models:
            created = await self.embedding_repo.create(model)
            created_list.append(
                FaceEmbeddingEntity(
                    id=created.id, user_id=created.user_id, embedding=created.embedding
                )
            )
        return created_list

    async def update_embedding(
        self, embedding_id: int, new_embedding: List[float]
    ) -> Optional[FaceEmbeddingEntity]:
        """Update embedding"""
        model = await self.embedding_repo.get_by_id(embedding_id)
        if not model:
            return None

        model.embedding = new_embedding
        updated = await self.embedding_repo.update(model)
        return FaceEmbeddingEntity(
            id=updated.id, user_id=updated.user_id, embedding=updated.embedding
        )

    async def delete_embedding(self, embedding_id: int) -> bool:
        """Delete embedding by ID"""
        return await self.embedding_repo.delete(embedding_id)

    async def delete_embeddings_by_user(self, user_id: int) -> bool:
        """Delete all embeddings for a user"""
        return await self.embedding_repo.delete_by_user(user_id)
