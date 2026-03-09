from app.application.services.department_service import DepartmentService
from app.domain.entities.department import Department
from typing import List, Optional


class CreateDepartmentUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self, name: str, manager_id: Optional[int] = None) -> Department:
        return await self.service.create_department(name, manager_id)


class GetDepartmentUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self, dept_id: int) -> Optional[Department]:
        dept = await self.service.get_department(dept_id)
        if not dept:
            raise ValueError(f"Department with ID {dept_id} not found")
        return dept


class ListDepartmentsUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self) -> List[Department]:
        return await self.service.list_departments()


class DeleteDepartmentUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self, dept_id: int) -> bool:
        deleted = await self.service.delete_department(dept_id)
        if not deleted:
            raise ValueError(f"Department with ID {dept_id} not found")
        return deleted


class AssignManagerUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self, dept_id: int, manager_id: int) -> Department:
        dept = await self.service.assign_manager(dept_id, manager_id)
        if not dept:
            raise ValueError(f"Department with ID {dept_id} not found")
        return dept
