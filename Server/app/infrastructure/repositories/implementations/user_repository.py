from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.infrastructure.db.models import User as UserModel
from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.interfaces.user_repository import IUserRepository


class UserRepository(BaseRepository[UserModel], IUserRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)
        print("UserRepository initialized")

    async def get(self, id: int) -> Optional[UserModel]:
        return await self.get_by_id(id)

    async def get_by_name(self, name: str) -> Optional[UserModel]:
        return await self.get_by_field("name", name)

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        return await self.get_by_field("username", username)

    async def list_by_department(self, dept_id: int) -> List[UserModel]:
        return await self.filter(department_id=dept_id)

    async def list_by_role(self, role: str) -> List[UserModel]:
        return await self.filter(role=role)

    async def create(self, user: UserModel) -> UserModel:
        try:
            print(f"Creating user: {user.name}")
            existing = await self.get_by_username(user.username)
            if existing:
                raise ValueError(f"User with UserName '{user.username}' already exists")

            result = await self.add(user)
            print(f"User created with ID: {result.id}")
            return result
        except Exception as e:
            print(f"Error in create: {e}")
            raise e

    async def update(self, user: UserModel) -> UserModel:
        try:
            return await super().update(user)
        except Exception as e:
            print(f"Error in update: {e}")
            raise e

    async def delete(self, user_id: int) -> bool:
        try:
            return await self.delete_by_id(user_id)
        except Exception as e:
            print(f"Error in delete: {e}")
            raise e

    async def list(self) -> List[UserModel]:
        return await self.get_all()
