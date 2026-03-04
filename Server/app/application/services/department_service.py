from typing import List, Optional
from app.infrastructure.repositories.implementations.department_repository import (
    DepartmentRepository,
)
from app.domain.entities.department import Department
from app.infrastructure.db.models import Department as DepartmentModel
from sqlalchemy.exc import IntegrityError


class DepartmentService:
    def __init__(self, dept_repo: DepartmentRepository):
        self.dept_repo = dept_repo

    async def get_department(self, dept_id: int) -> Optional[Department]:
        model = await self.dept_repo.get(dept_id)
        if not model:
            return None
        return Department(id=model.id, name=model.name, manager_id=model.manager_id)

    async def get_by_name(self, name: str) -> Optional[Department]:
        model = await self.dept_repo.get_by_name(name)
        if not model:
            return None
        return Department(id=model.id, name=model.name, manager_id=model.manager_id)

    async def list_departments(self) -> List[Department]:
        models = await self.dept_repo.list()
        return [
            Department(id=m.id, name=m.name, manager_id=m.manager_id) for m in models
        ]

    async def create_department(
        self, name: str, manager_id: Optional[int] = None
    ) -> Department:
        model = DepartmentModel(name=name, manager_id=manager_id)
        try:
            created = await self.dept_repo.create(model)
            return Department(
                id=created.id, name=created.name, manager_id=created.manager_id
            )
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to create department: {str(e)}")

    async def update_manager(
        self, dept_id: int, manager_id: int
    ) -> Optional[Department]:
        updated = await self.dept_repo.update_manager(dept_id, manager_id)
        if not updated:
            return None
        return Department(
            id=updated.id, name=updated.name, manager_id=updated.manager_id
        )

    async def delete_department(self, dept_id: int) -> bool:
        existing = await self.get_department(dept_id)
        if not existing:
            return False
        return await self.dept_repo.delete(dept_id)
