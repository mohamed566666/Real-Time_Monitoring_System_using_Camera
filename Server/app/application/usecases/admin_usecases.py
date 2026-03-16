from typing import List
from fastapi import HTTPException, status

from app.domain.entities.entities import AdminEntity, DashboardRole
from app.infrastructure.repositories.implementations.admin_repository import (
    AdminRepository,
)
from app.infrastructure.repositories.implementations.department_repository import (
    DepartmentRepository,
)
from app.application.services.auth_service import AuthService


class AdminUseCases:

    def __init__(self, admin_repo: AdminRepository, auth_service: AuthService):
        self.admin_repo = admin_repo
        self.auth_service = auth_service

    async def create_admin(self, username: str, password: str) -> AdminEntity:
        if await self.admin_repo.get_by_username(username):
            raise HTTPException(
                status_code=409, detail=f"Username '{username}' already exists"
            )
        return await self.admin_repo.create(
            AdminEntity(
                id=None,
                username=username,
                hashed_password=self.auth_service.hash_password(password),
                role=DashboardRole.ADMIN,
            )
        )

    async def get_admin(self, admin_id: int) -> AdminEntity:
        admin = await self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        return admin

    async def list_admins(self) -> List[AdminEntity]:
        return await self.admin_repo.get_all()

    async def delete_admin(self, admin_id: int) -> bool:
        if not await self.admin_repo.delete(admin_id):
            raise HTTPException(status_code=404, detail="Admin not found")
        return True
