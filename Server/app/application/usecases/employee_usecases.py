from typing import List, Optional
from fastapi import HTTPException

from app.domain.entities.entities import EmployeeEntity
from app.infrastructure.repositories.implementations.employee_repository import (
    EmployeeRepository,
)
from app.infrastructure.repositories.implementations.manager_repository import (
    ManagerRepository,
)
from app.infrastructure.repositories.implementations.department_repository import (
    DepartmentRepository,
)

DEV_MANAGER_ID = 2


class EmployeeUseCases:

    def __init__(
        self,
        employee_repo: EmployeeRepository,
        manager_repo: ManagerRepository,
        dept_repo: DepartmentRepository,
    ):
        self.employee_repo = employee_repo
        self.manager_repo = manager_repo
        self.dept_repo = dept_repo

    async def create_employee(
        self,
        name: str,
        username: str,
        manager_id: Optional[int] = None,
    ) -> EmployeeEntity:
        resolved_manager_id = manager_id or DEV_MANAGER_ID

        manager = await self.manager_repo.get_by_id(resolved_manager_id)
        if not manager:
            raise HTTPException(
                status_code=404, detail=f"Manager {resolved_manager_id} not found"
            )
        if not manager.department_id:
            raise HTTPException(
                status_code=400, detail="Manager has no department assigned yet"
            )
        if await self.employee_repo.get_by_username(username):
            raise HTTPException(
                status_code=409, detail=f"Username '{username}' already exists"
            )

        return await self.employee_repo.create(
            EmployeeEntity(
                id=None,
                name=name,
                username=username,
                department_id=manager.department_id,
                worked_hours=0.0,
            )
        )

    async def get_employee(self, employee_id: int) -> EmployeeEntity:
        emp = await self.employee_repo.get_by_id(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        return emp

    async def list_employees(self) -> List[EmployeeEntity]:
        return await self.employee_repo.get_all()

    async def list_by_department(self, department_id: int) -> List[EmployeeEntity]:
        return await self.employee_repo.get_by_department(department_id)


    async def add_worked_hours(self, employee_id: int, hours: float) -> EmployeeEntity:
        if hours <= 0:
            raise HTTPException(status_code=422, detail="hours must be positive")
        emp = await self.employee_repo.get_by_id(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        emp.worked_hours = round(emp.worked_hours + hours, 4)
        return await self.employee_repo.update(emp)

    async def set_worked_hours(self, employee_id: int, hours: float) -> EmployeeEntity:
        if hours < 0:
            raise HTTPException(status_code=422, detail="hours cannot be negative")
        emp = await self.employee_repo.get_by_id(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        emp.worked_hours = round(hours, 4)
        return await self.employee_repo.update(emp)

    async def reset_worked_hours(self, employee_id: int) -> EmployeeEntity:
        emp = await self.employee_repo.get_by_id(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        emp.worked_hours = 0.0
        return await self.employee_repo.update(emp)

    async def delete_employee(self, employee_id: int) -> bool:
        if not await self.employee_repo.delete(employee_id):
            raise HTTPException(status_code=404, detail="Employee not found")
        return True
