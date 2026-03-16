from typing import List, Optional
from fastapi import HTTPException, status

from app.domain.entities.entities import DashboardUserEntity, DashboardRole
from app.infrastructure.repositories.implementations.dashboard_user_repository import (
    DashboardUserRepository,
)
from app.infrastructure.repositories.implementations.department_repository import (
    DepartmentRepository,
)
from app.application.services.auth_service import AuthService


class DashboardUserUseCases:

    def __init__(
        self,
        user_repo: DashboardUserRepository,
        dept_repo: DepartmentRepository,
        auth_service: AuthService,
    ):
        self.user_repo = user_repo
        self.dept_repo = dept_repo
        self.auth_service = auth_service


    async def login(self, username: str, password: str) -> str:
        user = await self.user_repo.get_by_username(username)
        if not user or not self.auth_service.verify_password(
            password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        return self.auth_service.create_access_token(
            subject=str(user.id), role=user.role.value
        )


    async def create_user(
        self,
        username: str,
        password: str,
        role: DashboardRole,
        department_id: Optional[int] = None,
    ) -> DashboardUserEntity:
        if await self.user_repo.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{username}' already exists",
            )
        if department_id:
            if not await self.dept_repo.get_by_id(department_id):
                raise HTTPException(status_code=404, detail="Department not found")

        entity = DashboardUserEntity(
            id=None,
            username=username,
            hashed_password=self.auth_service.hash_password(password),
            role=role,
            department_id=department_id,
        )
        return await self.user_repo.create(entity)


    async def get_user(self, user_id: int) -> DashboardUserEntity:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def list_users(self) -> List[DashboardUserEntity]:
        return await self.user_repo.get_all()

    async def list_managers(self) -> List[DashboardUserEntity]:
        return await self.user_repo.get_all_managers()


    async def assign_department(
        self, manager_id: int, department_id: int
    ) -> DashboardUserEntity:
        user = await self.user_repo.get_by_id(manager_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.role != DashboardRole.MANAGER:
            raise HTTPException(
                status_code=400, detail="Only managers can be assigned to a department"
            )
        if not await self.dept_repo.get_by_id(department_id):
            raise HTTPException(status_code=404, detail="Department not found")
        user.department_id = department_id
        return await self.user_repo.update(user)


    async def delete_user(self, user_id: int) -> bool:
        if not await self.user_repo.delete(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        return True
