from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from app.application.services.department_service import DepartmentService
from app.application.usecases.department_usecases import (
    CreateDepartmentUseCase,
    GetDepartmentUseCase,
    ListDepartmentsUseCase,
    DeleteDepartmentUseCase,
    AssignManagerUseCase,
)
from app.core.dependencies import get_department_service


class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: int
    name: str
    manager_id: Optional[int] = None

    class Config:
        from_attributes = True


router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post(
    "/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_department(
    department: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
):
    use_case = CreateDepartmentUseCase(service)
    try:
        created = await use_case.execute(name=department.name, manager_id=None)
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[DepartmentResponse])
async def list_departments(
    service: DepartmentService = Depends(get_department_service),
):
    use_case = ListDepartmentsUseCase(service)
    departments = await use_case.execute()
    return departments


@router.delete("/{dept_id}")
async def delete_department(
    dept_id: int, service: DepartmentService = Depends(get_department_service)
):
    use_case = DeleteDepartmentUseCase(service)
    try:
        await use_case.execute(dept_id)
        return {"detail": "Department deleted"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{dept_id}/assign_manager/{manager_id}")
async def assign_manager(
    dept_id: int,
    manager_id: int,
    service: DepartmentService = Depends(get_department_service),
):
    use_case = AssignManagerUseCase(service)
    try:
        dept = await use_case.execute(dept_id, manager_id)
        return dept
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
