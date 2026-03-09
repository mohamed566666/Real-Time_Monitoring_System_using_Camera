from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


class ISessionRepository(ABC):

    @abstractmethod
    async def get(self, id: UUID): ...

    @abstractmethod
    async def get_by_id(self, id: UUID): ...

    @abstractmethod
    async def active(self) -> List: ...

    @abstractmethod
    async def by_user(self, user_id: int) -> List: ...

    @abstractmethod
    async def by_device(self, device_id: int) -> List: ...

    @abstractmethod
    async def create(self, session): ...

    @abstractmethod
    async def end(self, session_id: UUID, reason): ...

    @abstractmethod
    async def list(self) -> List: ...

    @abstractmethod
    async def list_active(self) -> List: ...
