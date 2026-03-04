from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List
from pydantic import BaseModel
import cv2
import numpy as np

from app.application.usecases.auth_use_cases import (
    VerifyUserIdentityUseCase,
    VerifyUserWithImageUseCase,
)
from app.core.dependencies import (
    get_verify_user_usecase,
    get_verify_user_with_image_usecase,
    get_embedding_service,
    get_face_engine,
)


class VerifyRequest(BaseModel):
    username: str
    embedding: List[float]


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/verify", response_model=List[float])
async def verify_user_identity(
    request: VerifyRequest,
    verify_usecase: VerifyUserIdentityUseCase = Depends(get_verify_user_usecase),
    embedding_service=Depends(get_embedding_service),
):
    try:
        user = await verify_usecase.user_service.get_user_by_username(request.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{request.username}' not found",
            )

        stored_embeddings = await embedding_service.get_embeddings_by_user(user.id)
        if not stored_embeddings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No face embedding found for user '{request.username}'",
            )

        stored_embedding = stored_embeddings[0]

        similarity = verify_usecase.face_engine.calculate_similarity(
            request.embedding, stored_embedding.embedding
        )

        if similarity < verify_usecase.similarity_threshold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Face verification failed - similarity: {similarity:.2f}",
            )

        return stored_embedding.embedding

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/verify-with-image", response_model=List[float])
async def verify_user_with_image(
    username: str = Form(...),
    image: UploadFile = File(...),
    verify_usecase: VerifyUserWithImageUseCase = Depends(
        get_verify_user_with_image_usecase
    ),
    embedding_service=Depends(get_embedding_service),
):

    try:
        contents = await image.read()

        user = await verify_usecase.verify_usecase.user_service.get_user_by_username(
            username
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{username}' not found",
            )

        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file"
            )

        face = verify_usecase.face_engine.detect_face(img)
        if face is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image",
            )

        stored_embeddings = await embedding_service.get_embeddings_by_user(user.id)
        if not stored_embeddings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No face embedding found for user '{username}'",
            )

        stored_embedding = stored_embeddings[0]

        verified, similarity = verify_usecase.face_engine.verify_face(
            face,
            stored_embedding.embedding,
            threshold=verify_usecase.verify_usecase.similarity_threshold,
        )

        if not verified:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Face verification failed - similarity: {similarity:.2f}",
            )

        return stored_embedding.embedding

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/compare-faces")
async def compare_faces(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    face_engine=Depends(get_face_engine),
):
    try:
        contents1 = await image1.read()
        nparr1 = np.frombuffer(contents1, np.uint8)
        img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)

        contents2 = await image2.read()
        nparr2 = np.frombuffer(contents2, np.uint8)
        img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

        if img1 is None or img2 is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file(s)"
            )

        face1 = face_engine.detect_face(img1)
        face2 = face_engine.detect_face(img2)

        if face1 is None or face2 is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not detect face in one or both images",
            )

        emb1 = face_engine.get_embedding(face1)
        emb2 = face_engine.get_embedding(face2)

        similarity = face_engine.calculate_similarity(emb1, emb2)

        return {
            "similarity": similarity,
            "is_same_person": similarity >= 0.6,
            "threshold": 0.6,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
