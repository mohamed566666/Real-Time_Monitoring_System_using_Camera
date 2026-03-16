from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_manager_usecases
from app.application.usecases.manager_usecases import ManagerUseCases
from app.domain.entities.entities import DashboardUserEntity

router = APIRouter(prefix="/managers", tags=["Managers"])


class AssignDept(BaseModel):
    department_id: int


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    department_id: Optional[int]
    created_at: datetime


def _schema(e: DashboardUserEntity) -> UserResponse:
    return UserResponse(
        id=e.id,
        username=e.username,
        role=e.role.value,
        department_id=e.department_id,
        created_at=e.created_at,
    )


@router.get("", response_model=List[UserResponse], summary="List managers")
async def list_managers(usecases: ManagerUseCases = Depends(get_manager_usecases)):
    return [_schema(e) for e in await usecases.list_managers()]


@router.get("/{manager_id}", response_model=UserResponse, summary="Get manager")
async def get_manager(
    manager_id: int, usecases: ManagerUseCases = Depends(get_manager_usecases)
):
    return _schema(await usecases.get_manager(manager_id))


@router.patch(
    "/{manager_id}/department", response_model=UserResponse, summary="Assign department"
)
async def assign_department(
    manager_id: int,
    body: AssignDept,
    usecases: ManagerUseCases = Depends(get_manager_usecases),
):
    return _schema(await usecases.assign_department(manager_id, body.department_id))
