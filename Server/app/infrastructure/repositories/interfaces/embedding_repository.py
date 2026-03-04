# app/infrastructure/repositories/interfaces/embedding_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from app.infrastructure.db.models import FaceEmbedding


class IFaceEmbeddingRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[FaceEmbedding]:
        """Get embedding by ID"""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: int) -> List[FaceEmbedding]:
        """Get all embeddings for a user"""
        pass

    @abstractmethod
    async def get_by_user_ids(self, user_ids: List[int]) -> List[FaceEmbedding]:
        """Get embeddings for multiple users"""
        pass

    @abstractmethod
    async def create(self, embedding: FaceEmbedding) -> FaceEmbedding:
        """Create new embedding"""
        pass

    @abstractmethod
    async def update(self, embedding: FaceEmbedding) -> FaceEmbedding:
        """Update embedding"""
        pass

    @abstractmethod
    async def delete(self, embedding_id: int) -> bool:
        """Delete embedding by ID"""
        pass

    @abstractmethod
    async def list_all(self) -> List[FaceEmbedding]:
        """List all embeddings"""
        pass

    @abstractmethod
    async def delete_by_user(self, user_id: int) -> bool:
        """Delete all embeddings for a user"""
        pass
