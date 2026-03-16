from datetime import datetime
from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from app.core.dependencies import (
    get_face_embedding_usecases,
    require_admin,
    require_manager,
    require_any_auth,
)
from app.application.usecases.face_embedding_usecases import FaceEmbeddingUseCases
from app.domain.entities.entities import FaceEmbeddingEntity
from app.core.config import settings

router = APIRouter(prefix="/embeddings", tags=["Face Embeddings"])


class EmbeddingResponse(BaseModel):
    # id: int
    # username: str
    # created_at: datetime
    embedding: list[float]


class VerifyResponse(BaseModel):
    username: str
    match: bool
    similarity: float


class CompareResponse(BaseModel):
    match: bool
    similarity: float
    threshold_used: float


async def _schema(
    entity: FaceEmbeddingEntity,
    usecases: FaceEmbeddingUseCases,
) -> EmbeddingResponse:
    emp = await usecases.employee_repo.get_by_id(entity.employee_id)
    return EmbeddingResponse(
        # id=entity.id,
        # username=emp.username if emp else str(entity.employee_id),
        # created_at=entity.created_at,
        embedding=entity.embedding,
    )


@router.post(
    "/{username}/register",
    response_model=EmbeddingResponse,
    summary="Register or replace face embedding by username (Manager/Admin)",
)
async def register_embedding(
    username: str,
    image: UploadFile = File(..., description="Face photo (JPEG / PNG)"),
    usecases: FaceEmbeddingUseCases = Depends(get_face_embedding_usecases),
    _: dict = Depends(require_manager),
):
    image_bytes = await image.read()
    entity = await usecases.register_embedding_by_username(username, image_bytes)
    return await _schema(entity, usecases)


@router.post(
    "/{username}/verify",
    response_model=VerifyResponse,
    summary="Verify a face photo against the stored embedding",
)
async def verify_embedding(
    username: str,
    image: UploadFile = File(..., description="Face photo (JPEG / PNG)"),
    usecases: FaceEmbeddingUseCases = Depends(get_face_embedding_usecases),
    _: dict = Depends(require_any_auth),
):
    image_bytes = await image.read()
    match, similarity = await usecases.verify_by_username(username, image_bytes)
    return VerifyResponse(
        username=username, match=match, similarity=round(similarity, 4)
    )


@router.get(
    "/{username}",
    response_model=EmbeddingResponse,
    summary="Get embedding metadata by username",
)
async def get_embedding(
    username: str,
    usecases: FaceEmbeddingUseCases = Depends(get_face_embedding_usecases),
    _: dict = Depends(require_any_auth),
):
    entity = await usecases.get_embedding_by_username(username)
    return await _schema(entity, usecases)


@router.delete(
    "/{username}",
    summary="Delete face embedding by username (Admin only)",
)
async def delete_embedding(
    username: str,
    usecases: FaceEmbeddingUseCases = Depends(get_face_embedding_usecases),
    _: dict = Depends(require_admin),
):
    await usecases.delete_embedding_by_username(username)
    return {"detail": f"Face embedding for '{username}' deleted"}


@router.post(
    "/debug/compare",
    response_model=CompareResponse,
    summary="[DEBUG] Compare two face photos — nothing stored",
)
async def debug_compare(
    image1: UploadFile = File(..., description="First face photo"),
    image2: UploadFile = File(..., description="Second face photo"),
    usecases: FaceEmbeddingUseCases = Depends(get_face_embedding_usecases),
):
    bytes1 = await image1.read()
    bytes2 = await image2.read()
    match, similarity = await usecases.compare_two_images(bytes1, bytes2)
    return CompareResponse(
        match=match,
        similarity=round(similarity, 4),
        threshold_used=settings.FACE_RECOGNITION_THRESHOLD,
    )


# @router.post(
#     "/debug/extract",
#     summary="[DEBUG] Extract embedding vector from a photo — nothing stored",
# )
# async def debug_extract(
#     image: UploadFile = File(..., description="Face photo (JPEG / PNG)"),
#     usecases: FaceEmbeddingUseCases = Depends(get_face_embedding_usecases),
# ):
#     import cv2
#     import numpy as np

#     image_bytes = await image.read()
#     nparr = np.frombuffer(image_bytes, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     if img is None:
#         from fastapi import HTTPException

#         raise HTTPException(status_code=422, detail="Could not decode image")

#     face = usecases.face_engine.detect_face(img)
#     if face is None:
#         from fastapi import HTTPException

#         raise HTTPException(status_code=422, detail="No face detected in image")

#     embedding = usecases.face_engine.get_embedding(face)
#     return {
#         "embedding_size": len(embedding),
#         "embedding": embedding,
#     }
