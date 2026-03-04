# app/infrastructure/repositories/base_repository.py
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.sql import exists
from sqlalchemy.exc import IntegrityError

from app.infrastructure.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository for all entities"""

    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get entity by ID"""
        query = select(self.model_class).where(self.model_class.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination"""
        query = select(self.model_class).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """Get entity by field value"""
        field = getattr(self.model_class, field_name)
        query = select(self.model_class).where(field == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def filter(self, **kwargs) -> List[ModelType]:
        """Filter entities by field values"""
        query = select(self.model_class)
        for key, value in kwargs.items():
            field = getattr(self.model_class, key)
            query = query.where(field == value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def exists(self, id: Any) -> bool:
        """Check if entity exists by ID"""
        query = select(exists().where(self.model_class.id == id))
        result = await self.session.execute(query)
        return result.scalar()

    async def count(self) -> int:
        """Count all entities"""
        query = select(func.count()).select_from(self.model_class)
        result = await self.session.execute(query)
        return result.scalar()

    async def add(self, entity: ModelType) -> ModelType:
        """Add new entity and commit"""
        try:
            print(f"Adding entity: {entity}")
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            print(f"Added successfully: {entity.id}")
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            print(f"IntegrityError: {e}")
            raise e
        except Exception as e:
            await self.session.rollback()
            print(f"Error adding entity: {e}")
            raise e

    async def add_all(self, entities: List[ModelType]) -> List[ModelType]:
        """Add multiple entities and commit"""
        try:
            self.session.add_all(entities)
            await self.session.commit()
            for entity in entities:
                await self.session.refresh(entity)
            return entities
        except IntegrityError as e:
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update(self, entity: ModelType) -> ModelType:
        """Update entity and commit"""
        try:
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete(self, entity: ModelType) -> bool:
        """Delete entity and commit"""
        try:
            await self.session.delete(entity)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_by_id(self, id: Any) -> bool:
        """Delete entity by ID and commit"""
        try:
            entity = await self.get_by_id(id)
            if entity:
                await self.session.delete(entity)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            raise e
