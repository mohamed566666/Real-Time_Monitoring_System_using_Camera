from app.infrastructure.db.models import Department
from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.interfaces.department_repository import (
    IDepartmentRepository,
)
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select


class DepartmentRepository(BaseRepository[Department], IDepartmentRepository):

    def __init__(self, session):
        super().__init__(session, Department)

    async def get(self, id) -> Optional[Department]:
        return await self.get_by_id(id)

    async def get_by_name(self, name) -> Optional[Department]:
        return await self.get_by_field("name", name)

    async def list(self) -> List[Department]:
        return await self.get_all()

    async def create(self, dept: Department) -> Department:
        try:
            self.session.add(dept)
            await self.session.commit()
            await self.session.refresh(dept)
            return dept
        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
                raise ValueError(f"Department with name '{dept.name}' already exists")
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to create department: {str(e)}")

    async def delete(self, dept_id: int) -> bool:
        try:
            dept = await self.get_by_id(dept_id)
            if dept:
                await self.session.delete(dept)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update_manager(
        self, dept_id: int, manager_id: int
    ) -> Optional[Department]:
        try:
            dept = await self.get_by_id(dept_id)
            if not dept:
                return None

            dept.manager_id = manager_id
            await self.session.commit()
            await self.session.refresh(dept)
            return dept
        except Exception as e:
            await self.session.rollback()
            raise e
