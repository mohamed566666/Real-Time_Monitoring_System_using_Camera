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

from app.application.usecases.user_usecases import (
    CreateUserWithImageUseCase,
    GetUserUseCase,
    GetUserByNameUseCase,
    GetUserByUsernameUseCase,
    GetUserWithEmbeddingsUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase,
    DeleteUserWithEmbeddingsUseCase,
    ListUsersUseCase,
    ListUsersByRoleUseCase,
    ListUsersByDepartmentUseCase,
)


from app.core.dependencies import (
    get_create_user_with_image_usecase,
    get_get_user_usecase,
    get_get_user_by_name_usecase,
    get_get_user_by_username_usecase,
    get_get_user_with_embeddings_usecase,
    get_update_user_usecase,
    get_delete_user_usecase,
    get_delete_user_with_embeddings_usecase,
    get_list_users_usecase,
    get_list_users_by_role_usecase,
    get_list_users_by_department_usecase,
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
    use_case: CreateUserWithImageUseCase = Depends(get_create_user_with_image_usecase),
):
    try:
        contents = await image.read()

        created = await use_case.execute(
            name=name,
            username=username,
            image_bytes=contents,
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
    list_all_usecase: ListUsersUseCase = Depends(get_list_users_usecase),
    list_by_role_usecase: ListUsersByRoleUseCase = Depends(
        get_list_users_by_role_usecase
    ),
    list_by_dept_usecase: ListUsersByDepartmentUseCase = Depends(
        get_list_users_by_department_usecase
    ),
):
    try:
        if role:
            users = await list_by_role_usecase.execute(role=role)
        elif department_id:
            users = await list_by_dept_usecase.execute(dept_id=department_id)
        else:
            users = await list_all_usecase.execute()
        return users
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    use_case: GetUserUseCase = Depends(get_get_user_usecase),
):
    try:
        user = await use_case.execute(user_id=user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/by-name/{name}", response_model=UserResponse)
async def get_user_by_name(
    name: str,
    use_case: GetUserByNameUseCase = Depends(get_get_user_by_name_usecase),
):
    try:
        user = await use_case.execute(name=name)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    use_case: GetUserByUsernameUseCase = Depends(get_get_user_by_username_usecase),
):
    try:
        user = await use_case.execute(username=username)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/{user_id}/with-embeddings", response_model=UserWithEmbeddingsResponse)
async def get_user_with_embeddings(
    user_id: int,
    use_case: GetUserWithEmbeddingsUseCase = Depends(
        get_get_user_with_embeddings_usecase
    ),
):
    try:
        user_data = await use_case.execute(user_id=user_id)
        return user_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    use_case: UpdateUserUseCase = Depends(get_update_user_usecase),
):
    try:
        updated = await use_case.execute(
            user_id=user_id,
            name=user_update.name,
            role=user_update.role,
            department_id=user_update.department_id,
        )
        return updated
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_with_embeddings(
    user_id: int,
    use_case: DeleteUserWithEmbeddingsUseCase = Depends(
        get_delete_user_with_embeddings_usecase
    ),
):
    try:
        await use_case.execute(user_id=user_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/department/{dept_id}", response_model=List[UserResponse])
async def get_users_by_department(
    dept_id: int,
    use_case: ListUsersByDepartmentUseCase = Depends(
        get_list_users_by_department_usecase
    ),
):
    try:
        users = await use_case.execute(dept_id=dept_id)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/role/{role}", response_model=List[UserResponse])
async def get_users_by_role(
    role: str,
    use_case: ListUsersByRoleUseCase = Depends(get_list_users_by_role_usecase),
):
    try:
        users = await use_case.execute(role=role)
        return users
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
