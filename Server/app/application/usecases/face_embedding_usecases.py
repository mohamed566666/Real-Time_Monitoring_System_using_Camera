import cv2
import numpy as np
from fastapi import HTTPException, status

from app.domain.entities.entities import FaceEmbeddingEntity
from app.infrastructure.repositories.implementations.face_embedding_repository import (
    FaceEmbeddingRepository,
)
from app.infrastructure.repositories.implementations.employee_repository import (
    EmployeeRepository,
)
from app.infrastructure.aiModels.face_engine import FaceEngine


def _decode_face(image_bytes: bytes, face_engine: FaceEngine):
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not decode image",
        )
    face = face_engine.detect_face(image)
    if face is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No face detected in image",
        )
    return face


class FaceEmbeddingUseCases:

    def __init__(
        self,
        embedding_repo: FaceEmbeddingRepository,
        employee_repo: EmployeeRepository,
        face_engine: FaceEngine,
    ):
        self.embedding_repo = embedding_repo
        self.employee_repo = employee_repo
        self.face_engine = face_engine

    async def register_embedding_by_username(
        self, username: str, image_bytes: bytes
    ) -> FaceEmbeddingEntity:
        emp = await self.employee_repo.get_by_username(username)
        if not emp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with username '{username}' not found",
            )

        face = _decode_face(image_bytes, self.face_engine)
        embedding = self.face_engine.get_embedding(face)

        existing = await self.embedding_repo.get_by_employee_id(emp.id)
        if existing:
            existing.embedding = embedding
            return await self.embedding_repo.update(existing)

        entity = FaceEmbeddingEntity(id=None, employee_id=emp.id, embedding=embedding)
        return await self.embedding_repo.create(entity)

    async def verify_by_username(
        self, username: str, image_bytes: bytes
    ) -> tuple[bool, float]:
        stored = await self.embedding_repo.get_by_username(username)
        if not stored:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No embedding registered for username '{username}'",
            )
        face = _decode_face(image_bytes, self.face_engine)
        return self.face_engine.verify_face(face, stored.embedding)

    async def compare_two_images(
        self, image_bytes_1: bytes, image_bytes_2: bytes
    ) -> tuple[bool, float]:
        face1 = _decode_face(image_bytes_1, self.face_engine)
        face2 = _decode_face(image_bytes_2, self.face_engine)

        emb1 = self.face_engine.get_embedding(face1)
        emb2 = self.face_engine.get_embedding(face2)

        similarity = self.face_engine.calculate_similarity(emb1, emb2)
        match = similarity >= 0.4
        return match, similarity

    async def get_embedding_by_username(self, username: str) -> FaceEmbeddingEntity:
        emb = await self.embedding_repo.get_by_username(username)
        if not emb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No embedding registered for username '{username}'",
            )
        return emb

    async def delete_embedding_by_username(self, username: str) -> bool:
        emb = await self.embedding_repo.get_by_username(username)
        if not emb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No embedding registered for username '{username}'",
            )
        return await self.embedding_repo.delete(emb.id)
