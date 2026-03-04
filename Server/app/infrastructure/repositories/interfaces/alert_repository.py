from abc import ABC, abstractmethod


class IAlertRepository(ABC):

    @abstractmethod
    async def create(self, alert): ...

    @abstractmethod
    async def by_session(self, session_id): ...
