from typing import List, Optional
from fastapi import HTTPException, status

from app.domain.entities.entities import ManagerEntity, DashboardRole
from app.infrastructure.repositories.implementations.manager_repository import (
    ManagerRepository,
)
from app.infrastructure.repositories.implementations.department_repository import (
    DepartmentRepository,
)
from app.application.services.auth_service import AuthService


class ManagerUseCases:

    def __init__(
        self,
        manager_repo: ManagerRepository,
        dept_repo: DepartmentRepository,
        auth_service: AuthService,
    ):
        self.manager_repo = manager_repo
        self.dept_repo = dept_repo
        self.auth_service = auth_service

    async def create_manager(
        self,
        username: str,
        password: str,
        department_id: Optional[int] = None,
    ) -> ManagerEntity:
        if await self.manager_repo.get_by_username(username):
            raise HTTPException(
                status_code=409, detail=f"Username '{username}' already exists"
            )
        if department_id and not await self.dept_repo.get_by_id(department_id):
            raise HTTPException(status_code=404, detail="Department not found")
        return await self.manager_repo.create(
            ManagerEntity(
                id=None,
                username=username,
                hashed_password=self.auth_service.hash_password(password),
                role=DashboardRole.MANAGER,
                department_id=department_id,
            )
        )

    async def get_manager(self, manager_id: int) -> ManagerEntity:
        m = await self.manager_repo.get_by_id(manager_id)
        if not m:
            raise HTTPException(status_code=404, detail="Manager not found")
        return m

    async def list_managers(self) -> List[ManagerEntity]:
        return await self.manager_repo.get_all()

    async def assign_department(
        self, manager_id: int, department_id: int
    ) -> ManagerEntity:
        m = await self.manager_repo.get_by_id(manager_id)
        if not m:
            raise HTTPException(status_code=404, detail="Manager not found")
        if not await self.dept_repo.get_by_id(department_id):
            raise HTTPException(status_code=404, detail="Department not found")
        m.department_id = department_id
        return await self.manager_repo.update(m)

    async def delete_manager(self, manager_id: int) -> bool:
        if not await self.manager_repo.delete(manager_id):
            raise HTTPException(status_code=404, detail="Manager not found")
        return True
