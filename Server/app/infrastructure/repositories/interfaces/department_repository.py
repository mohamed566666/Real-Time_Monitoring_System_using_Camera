from abc import ABC, abstractmethod
from app.infrastructure.db.models import Department
from typing import List, Optional


class IDepartmentRepository(ABC):

    @abstractmethod
    async def get(self, id: int) -> Optional[Department]: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Department]: ...

    @abstractmethod
    async def list(self) -> List[Department]: ...

    @abstractmethod
    async def create(self, dept: Department) -> Department: ...

    @abstractmethod
    async def delete(self, dept_id: int) -> bool: ...

    @abstractmethod
    async def update_manager(
        self, dept_id: int, manager_id: int
    ) -> Optional[Department]: ...
