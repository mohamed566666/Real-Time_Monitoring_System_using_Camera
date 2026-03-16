from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, Field

from app.core.dependencies import get_employee_usecases, get_face_embedding_usecases
from app.application.usecases.employee_usecases import EmployeeUseCases
from app.application.usecases.face_embedding_usecases import FaceEmbeddingUseCases
from app.domain.entities.entities import EmployeeEntity

router = APIRouter(prefix="/employees", tags=["Employees"])



class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    # TODO: remove manager_id when auth is enabled — will come from JWT
    manager_id: Optional[int] = None


class WorkedHoursSet(BaseModel):
    hours: float = Field(..., ge=0)


class WorkedHoursAdd(BaseModel):
    hours: float = Field(..., gt=0)


class EmployeeResponse(BaseModel):
    id: int
    name: str
    username: str
    department_id: Optional[int]
    worked_hours: float
    is_online: bool
    created_at: datetime


class EmployeeRegisterResponse(BaseModel):
    employee: EmployeeResponse
    embedding_registered: bool


def _schema(e: EmployeeEntity) -> EmployeeResponse:
    return EmployeeResponse(
        id=e.id,
        name=e.name,
        username=e.username,
        department_id=e.department_id,
        worked_hours=e.worked_hours,
        is_online=e.is_online,
        created_at=e.created_at,
    )



@router.post(
    "/register",
    response_model=EmployeeRegisterResponse,
    summary="Register employee + face photo (department auto from manager)",
)
async def register_employee_with_photo(
    name: str = Form(..., min_length=2, max_length=100),
    username: str = Form(..., min_length=3, max_length=50),
    # TODO: remove manager_id when auth enabled — will come from JWT
    manager_id: Optional[int] = Form(default=None),
    photo: UploadFile = File(..., description="Face photo (JPEG / PNG)"),
    emp_usecases: EmployeeUseCases = Depends(get_employee_usecases),
    emb_usecases: FaceEmbeddingUseCases = Depends(get_face_embedding_usecases),
):
    employee = await emp_usecases.create_employee(name, username, manager_id)
    image_bytes = await photo.read()
    await emb_usecases.register_embedding_by_username(username, image_bytes)
    return EmployeeRegisterResponse(
        employee=_schema(employee), embedding_registered=True
    )



@router.post(
    "", response_model=EmployeeResponse, summary="Create employee without photo"
)
async def create_employee(
    body: EmployeeCreate,
    usecases: EmployeeUseCases = Depends(get_employee_usecases),
):
    return _schema(
        await usecases.create_employee(body.name, body.username, body.manager_id)
    )


@router.get("", response_model=List[EmployeeResponse], summary="List all employees")
async def list_employees(usecases: EmployeeUseCases = Depends(get_employee_usecases)):
    return [_schema(e) for e in await usecases.list_employees()]


@router.get(
    "/department/{dept_id}",
    response_model=List[EmployeeResponse],
    summary="List by department",
)
async def list_by_department(
    dept_id: int, usecases: EmployeeUseCases = Depends(get_employee_usecases)
):
    return [_schema(e) for e in await usecases.list_by_department(dept_id)]


@router.get(
    "/{employee_id}", response_model=EmployeeResponse, summary="Get employee by ID"
)
async def get_employee(
    employee_id: int, usecases: EmployeeUseCases = Depends(get_employee_usecases)
):
    return _schema(await usecases.get_employee(employee_id))



@router.patch(
    "/{employee_id}/hours/add",
    response_model=EmployeeResponse,
    summary="Add worked hours",
)
async def add_worked_hours(
    employee_id: int,
    body: WorkedHoursAdd,
    usecases: EmployeeUseCases = Depends(get_employee_usecases),
):
    return _schema(await usecases.add_worked_hours(employee_id, body.hours))


@router.patch(
    "/{employee_id}/hours/set",
    response_model=EmployeeResponse,
    summary="Set worked hours",
)
async def set_worked_hours(
    employee_id: int,
    body: WorkedHoursSet,
    usecases: EmployeeUseCases = Depends(get_employee_usecases),
):
    return _schema(await usecases.set_worked_hours(employee_id, body.hours))


@router.patch(
    "/{employee_id}/hours/reset",
    response_model=EmployeeResponse,
    summary="Reset worked hours",
)
async def reset_worked_hours(
    employee_id: int,
    usecases: EmployeeUseCases = Depends(get_employee_usecases),
):
    return _schema(await usecases.reset_worked_hours(employee_id))



@router.delete("/{employee_id}", summary="Delete employee")
async def delete_employee(
    employee_id: int,
    usecases: EmployeeUseCases = Depends(get_employee_usecases),
):
    await usecases.delete_employee(employee_id)
    return {"detail": "Employee deleted"}
