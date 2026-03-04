from abc import ABC, abstractmethod
from typing import Optional, List
from app.infrastructure.db.models import User


class IUserRepository(ABC):

    @abstractmethod
    async def get(self, id: int) -> Optional[User]: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[User]: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]: ...

    @abstractmethod
    async def list_by_department(self, dept_id: int) -> List[User]: ...

    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user: User) -> bool: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def list(self) -> List[User]: ...
