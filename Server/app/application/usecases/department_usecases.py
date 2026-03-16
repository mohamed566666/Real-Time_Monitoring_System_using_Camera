from typing import List
from fastapi import HTTPException, status

from app.domain.entities.entities import DepartmentEntity
from app.infrastructure.repositories.implementations.department_repository import (
    DepartmentRepository,
)


class DepartmentUseCases:

    def __init__(self, dept_repo: DepartmentRepository):
        self.dept_repo = dept_repo

    async def create_department(self, name: str) -> DepartmentEntity:
        existing = await self.dept_repo.get_by_name(name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Department '{name}' already exists",
            )
        return await self.dept_repo.create(DepartmentEntity(id=None, name=name))

    async def get_department(self, department_id: int) -> DepartmentEntity:
        dept = await self.dept_repo.get_by_id(department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )
        return dept

    async def list_departments(self) -> List[DepartmentEntity]:
        return await self.dept_repo.get_all()

    async def rename_department(
        self, department_id: int, new_name: str
    ) -> DepartmentEntity:
        dept = await self.dept_repo.get_by_id(department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )
        dept.name = new_name
        return await self.dept_repo.update(dept)

    async def delete_department(self, department_id: int) -> bool:
        deleted = await self.dept_repo.delete(department_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )
        return True
