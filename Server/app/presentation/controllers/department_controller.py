from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_dept_usecases, require_admin
from app.application.usecases.department_usecases import DepartmentUseCases
from app.domain.entities.entities import DepartmentEntity

router = APIRouter(prefix="/departments", tags=["Departments"])


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class DepartmentUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class DepartmentResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


def _schema(e: DepartmentEntity) -> DepartmentResponse:
    return DepartmentResponse(id=e.id, name=e.name)


@router.post("", response_model=DepartmentResponse, summary="Create a department")
async def create_department(
    body: DepartmentCreate,
    usecases: DepartmentUseCases = Depends(get_dept_usecases),
    _: dict = Depends(require_admin),
):
    return _schema(await usecases.create_department(body.name))


@router.get("", response_model=List[DepartmentResponse], summary="List all departments")
async def list_departments(
    usecases: DepartmentUseCases = Depends(get_dept_usecases),
    _: dict = Depends(require_admin),
):
    return [_schema(e) for e in await usecases.list_departments()]


@router.get("/{dept_id}", response_model=DepartmentResponse, summary="Get a department")
async def get_department(
    dept_id: int,
    usecases: DepartmentUseCases = Depends(get_dept_usecases),
    _: dict = Depends(require_admin),
):
    return _schema(await usecases.get_department(dept_id))


@router.patch(
    "/{dept_id}", response_model=DepartmentResponse, summary="Rename a department"
)
async def rename_department(
    dept_id: int,
    body: DepartmentUpdate,
    usecases: DepartmentUseCases = Depends(get_dept_usecases),
    _: dict = Depends(require_admin),
):
    return _schema(await usecases.rename_department(dept_id, body.name))


@router.delete("/{dept_id}", summary="Delete a department")
async def delete_department(
    dept_id: int,
    usecases: DepartmentUseCases = Depends(get_dept_usecases),
    _: dict = Depends(require_admin),
):
    await usecases.delete_department(dept_id)
    return {"detail": "Department deleted"}
