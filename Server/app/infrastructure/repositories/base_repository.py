from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):

    @abstractmethod
    async def get_by_id(self, entity_id) -> Optional[T]: ...

    @abstractmethod
    async def get_all(self) -> List[T]: ...

    @abstractmethod
    async def create(self, entity: T) -> T: ...

    @abstractmethod
    async def update(self, entity: T) -> T: ...

    @abstractmethod
    async def delete(self, entity_id) -> bool: ...
