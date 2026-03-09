from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
import cv2
import numpy as np
from uuid import UUID

from app.application.usecases.auth_use_cases import (
    VerifyUserIdentityUseCase,
    VerifyUserWithImageUseCase,
)
from app.application.services.session_service import SessionService
from app.application.services.device_service import DeviceService
from app.core.dependencies import (
    get_verify_user_usecase,
    get_verify_user_with_image_usecase,
    get_embedding_service,
    get_face_engine,
    get_session_service_for_controller,
    get_device_service_for_controller,
)


class LoginRequest(BaseModel):
    username: str
    embedding: List[float]
    device_name: str


class LogoutRequest(BaseModel):
    username: str
    device_name: str
    session_id: Optional[UUID] = None


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=dict)
async def login(
    request: LoginRequest,
    verify_usecase: VerifyUserIdentityUseCase = Depends(get_verify_user_usecase),
    embedding_service=Depends(get_embedding_service),
    session_service: SessionService = Depends(get_session_service_for_controller),
    device_service: DeviceService = Depends(get_device_service_for_controller),
):
    try:
        device = await device_service.get_device_by_name(request.device_name)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device '{request.device_name}' not found",
            )

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
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Face verification failed - similarity: {similarity:.2f}",
            )

        active_session = await session_service.get_active_session(user.id)

        if active_session:
            await session_service.force_end_session(
                active_session.id, reason="new_session_started"
            )

        new_session = await session_service.start_session(
            user_id=user.id, device_id=device.id
        )

        return {
            "success": True,
            "message": "User verified successfully",
            "embedding": stored_embedding.embedding,
            "session_id": str(new_session.id),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


# @router.post("/login-with-image", response_model=dict)
# async def login_user_with_image_for_debugging(
#     username: str = Form(...),
#     device_name: str = Form(...),
#     image: UploadFile = File(...),
#     verify_usecase: VerifyUserWithImageUseCase = Depends(
#         get_verify_user_with_image_usecase
#     ),
#     embedding_service=Depends(get_embedding_service),
#     session_service: SessionService = Depends(get_session_service_for_controller),
#     device_service: DeviceService = Depends(get_device_service_for_controller),
# ):
#     try:
#         device = await device_service.get_device_by_name(device_name)
#         if not device:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Device '{device_name}' not found",
#             )

#         contents = await image.read()

#         user = await verify_usecase.verify_usecase.user_service.get_user_by_username(
#             username
#         )
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"User '{username}' not found",
#             )

#         nparr = np.frombuffer(contents, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         if img is None:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file"
#             )

#         face = verify_usecase.face_engine.detect_face(img)
#         if face is None:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="No face detected in the image",
#             )

#         stored_embeddings = await embedding_service.get_embeddings_by_user(user.id)
#         if not stored_embeddings:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No face embedding found for user '{username}'",
#             )

#         stored_embedding = stored_embeddings[0]

#         verified, similarity = verify_usecase.face_engine.verify_face(
#             face,
#             stored_embedding.embedding,
#             threshold=verify_usecase.verify_usecase.similarity_threshold,
#         )

#         if not verified:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail=f"Face verification failed - similarity: {similarity:.2f}",
#             )

#         active_session = await session_service.get_active_session(user.id)

#         if active_session:
#             await session_service.force_end_session(
#                 active_session.id, reason="new_session_started"
#             )

#         new_session = await session_service.start_session(
#             user_id=user.id, device_id=device.id
#         )

#         return {
#             "success": True,
#             "message": "User verified successfully",
#             "embedding": stored_embedding.embedding,
#             "session_id": str(new_session.id),
#         }

#     except HTTPException:
#         raise
#     except ValueError as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal server error: {str(e)}",
#         )


@router.post("/logout", response_model=dict)
async def logout(
    request: LogoutRequest,
    session_service: SessionService = Depends(get_session_service_for_controller),
    device_service: DeviceService = Depends(get_device_service_for_controller),
    verify_usecase: VerifyUserIdentityUseCase = Depends(get_verify_user_usecase),
):
    try:
        device = await device_service.get_device_by_name(request.device_name)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device '{request.device_name}' not found",
            )

        user = await verify_usecase.user_service.get_user_by_username(request.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{request.username}' not found",
            )

        if request.session_id:
            session = await session_service.get_session(request.session_id)

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session '{request.session_id}' not found",
                )

            if session.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session does not belong to this user",
                )

            await session_service.force_end_session(session.id, reason="logout")

            return {
                "success": True,
                "message": "Logged out successfully",
                "session_id": str(session.id),
            }

        else:
            active_session = await session_service.get_active_session(user.id)
            if not active_session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active session found for this user",
                )
            await session_service.force_end_session(active_session.id, reason="logout")
            return {
                "success": True,
                "message": "Logged out successfully",
                "session_id": str(active_session.id),
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


# @router.post("/compare-faces")
# async def compare_faces(
#     image1: UploadFile = File(...),
#     image2: UploadFile = File(...),
#     face_engine=Depends(get_face_engine),
# ):
#     try:
#         contents1 = await image1.read()
#         nparr1 = np.frombuffer(contents1, np.uint8)
#         img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)

#         contents2 = await image2.read()
#         nparr2 = np.frombuffer(contents2, np.uint8)
#         img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

#         if img1 is None or img2 is None:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file(s)"
#             )

#         face1 = face_engine.detect_face(img1)
#         face2 = face_engine.detect_face(img2)

#         if face1 is None or face2 is None:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Could not detect face in one or both images",
#             )

#         emb1 = face_engine.get_embedding(face1)
#         emb2 = face_engine.get_embedding(face2)

#         similarity = face_engine.calculate_similarity(emb1, emb2)

#         return {
#             "similarity": similarity,
#             "is_same_person": similarity >= 0.6,
#             "threshold": 0.6,
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )
