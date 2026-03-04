# app/application/use_cases/user_use_cases.py
from app.application.services.user_service import UserService
from typing import List, Optional
from app.domain.entities.user import UserEntity


class CreateUserUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(
        self,
        name: str,
        username: str,
        role: str = "employee",
        department_id: Optional[int] = None,
    ):
        try:
            return await self.service.create_user(name, username, role, department_id)
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to create user: {str(e)}")


class GetUserUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> UserEntity:
        user = await self.service.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user


class UpdateUserUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(
        self,
        user_id: int,
        name: Optional[str] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        department_id: Optional[int] = None,
    ) -> UserEntity:
        updated = await self.service.update_user(
            user_id, name, username, role, department_id
        )
        if not updated:
            raise ValueError(f"User with ID {user_id} not found")
        return updated


class DeleteUserUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> bool:
        deleted = await self.service.delete_user(user_id)
        if not deleted:
            raise ValueError(f"User with ID {user_id} not found")
        return deleted


class ListUsersUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self) -> List[UserEntity]:
        return await self.service.list_users()


class ListUsersByRoleUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, role: str) -> List[UserEntity]:
        return await self.service.list_users_by_role(role)


class ListUsersByDepartmentUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, dept_id: int) -> List[UserEntity]:
        return await self.service.list_users_by_department(dept_id)
