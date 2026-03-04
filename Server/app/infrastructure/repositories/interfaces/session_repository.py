from abc import ABC, abstractmethod


class ISessionRepository(ABC):

    @abstractmethod
    async def get(self, id): ...

    @abstractmethod
    async def active(self): ...

    @abstractmethod
    async def by_user(self, user_id: int): ...

    @abstractmethod
    async def create(self, session): ...

    @abstractmethod
    async def end(self, session_id, reason): ...