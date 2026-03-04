from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    UploadFile,
    File,
    Form,
)
from typing import List, Optional
from pydantic import BaseModel, Field
import cv2
import numpy as np

from app.application.services.user_service import UserService
from app.core.dependencies import (
    get_user_service_for_controller,
    get_user_service_with_embedding_for_controller,
    get_face_engine,
)


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field("employee")
    department_id: Optional[int] = Field(None)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    role: Optional[str] = Field(None)
    department_id: Optional[int] = Field(None)


class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    role: str
    department_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserWithEmbeddingsResponse(BaseModel):
    user: UserResponse
    embeddings: List[dict]
    embeddings_count: int


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    name: str = Form(..., min_length=3, max_length=100),
    username: str = Form(..., min_length=3, max_length=50),
    role: str = Form("employee"),
    department_id: Optional[int] = Form(None),
    image: UploadFile = File(...),
    service: UserService = Depends(get_user_service_with_embedding_for_controller),
    face_engine=Depends(get_face_engine),
):
    try:
        contents = await image.read()

        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file"
            )

        face = face_engine.detect_face(img)
        if face is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image. Please upload a clear face image.",
            )

        embedding = face_engine.get_embedding(face)

        created = await service.create_user_with_embedding(
            name=name,
            username=username,
            embedding=embedding,
            role=role,
            department_id=department_id,
        )

        return created

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    service: UserService = Depends(get_user_service_for_controller),
):
    role = role.upper() if role else None
    try:
        if role:
            users = await service.list_users_by_role(role)
        elif department_id:
            users = await service.list_users_by_department(department_id)
        else:
            users = await service.list_users()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service_for_controller),
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user


@router.get("/by-name/{name}", response_model=UserResponse)
async def get_user_by_name(
    name: str,
    service: UserService = Depends(get_user_service_for_controller),
):
    user = await service.get_user_by_name(name)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with name '{name}' not found",
        )
    return user


@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    service: UserService = Depends(get_user_service_for_controller),
):
    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{username}' not found",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service_for_controller),
):
    try:
        updated = await service.update_user(
            user_id=user_id,
            name=user_update.name,
            role=user_update.role,
            department_id=user_update.department_id,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service_for_controller),
):
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return None


@router.get("/department/{dept_id}", response_model=List[UserResponse])
async def get_users_by_department(
    dept_id: int,
    service: UserService = Depends(get_user_service_for_controller),
):
    users = await service.list_users_by_department(dept_id)
    return users


@router.get("/role/{role}", response_model=List[UserResponse])
async def get_users_by_role(
    role: str,
    service: UserService = Depends(get_user_service_for_controller),
):
    role = role.upper()
    users = await service.list_users_by_role(role)
    return users
