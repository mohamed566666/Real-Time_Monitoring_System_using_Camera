from app.application.services.department_service import DepartmentService


class CreateDepartmentUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self, name: str, manager_id: int = None):
        try:
            return await self.service.create_department(name, manager_id)
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to create department: {str(e)}")


class AssignManagerUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self, dept_id: int, manager_id: int):
        dept = await self.service.update_manager(dept_id, manager_id)
        if not dept:
            raise ValueError("Department not found")
        return dept


class DeleteDepartmentUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self, dept_id: int):
        deleted = await self.service.delete_department(dept_id)
        if not deleted:
            raise ValueError("Department not found")
        return deleted


class ListDepartmentsUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self):
        return await self.service.list_departments()


class GetDepartmentUseCase:
    def __init__(self, service: DepartmentService):
        self.service = service

    async def execute(self, dept_id: int):
        dept = await self.service.get_department(dept_id)
        if not dept:
            raise ValueError("Department not found")
        return dept
