from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import (
    get_admin_usecases,
    get_manager_usecases,
    require_admin,
)
from app.application.usecases.admin_usecases import AdminUseCases
from app.application.usecases.manager_usecases import ManagerUseCases
from app.domain.entities.entities import DashboardUserEntity

router = APIRouter(prefix="/admin", tags=["Admin"])


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class ManagerCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    department_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime


def _schema(e) -> UserResponse:
    return UserResponse(
        id=e.id,
        username=e.username,
        role=e.role.value,
        created_at=e.created_at,
    )



@router.post(
    "/seed",
    response_model=UserResponse,
    summary="Create first admin — no auth needed",
)
async def bootstrap(
    body: UserCreate,
    usecases: AdminUseCases = Depends(get_admin_usecases),
):
    return _schema(await usecases.create_admin(body.username, body.password))


@router.post("", response_model=UserResponse, summary="Create admin")
async def create_admin(
    body: UserCreate,
    usecases: AdminUseCases = Depends(get_admin_usecases),
):
    return _schema(await usecases.create_admin(body.username, body.password))


@router.get("", response_model=List[UserResponse], summary="List admins")
async def list_admins(usecases: AdminUseCases = Depends(get_admin_usecases)):
    return [_schema(e) for e in await usecases.list_admins()]


@router.get("/{admin_id}", response_model=UserResponse, summary="Get admin")
async def get_admin(
    admin_id: int, usecases: AdminUseCases = Depends(get_admin_usecases)
):
    return _schema(await usecases.get_admin(admin_id))


@router.delete("/{admin_id}", summary="Delete admin")
async def delete_admin(
    admin_id: int, usecases: AdminUseCases = Depends(get_admin_usecases)
):
    await usecases.delete_admin(admin_id)
    return {"detail": "Admin deleted"}


@router.post(
    "/managers", response_model=UserResponse, summary="Create manager (Admin action)"
)
async def create_manager(
    body: ManagerCreate,
    usecases: ManagerUseCases = Depends(get_manager_usecases),
):
    return _schema(
        await usecases.create_manager(body.username, body.password, body.department_id)
    )


@router.delete("/managers/{manager_id}", summary="Delete manager (Admin action)")
async def delete_manager(
    manager_id: int, usecases: ManagerUseCases = Depends(get_manager_usecases)
):
    await usecases.delete_manager(manager_id)
    return {"detail": "Manager deleted"}
