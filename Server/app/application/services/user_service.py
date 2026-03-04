from typing import List, Optional
from app.infrastructure.repositories.implementations.user_repository import (
    UserRepository,
)
from app.application.services.face_embedding_service import FaceEmbeddingService
from app.domain.entities.user import UserEntity
from app.infrastructure.db.models import User as UserModel


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        embedding_service: Optional[FaceEmbeddingService] = None,
    ):
        self.user_repo = user_repo
        self.embedding_service = embedding_service

    async def get_user(self, user_id: int) -> Optional[UserEntity]:
        model = await self.user_repo.get(user_id)
        if not model:
            return None

        return UserEntity(
            id=model.id,
            name=model.name,
            username=model.username,
            role=model.role.value if hasattr(model.role, "value") else model.role,
            department_id=model.department_id,
            created_at=model.created_at if hasattr(model, "created_at") else None,
        )

    async def get_user_by_name(self, name: str) -> Optional[UserEntity]:
        model = await self.user_repo.get_by_name(name)
        if not model:
            return None

        return UserEntity(
            id=model.id,
            name=model.name,
            username=model.username,
            role=model.role.value if hasattr(model.role, "value") else model.role,
            department_id=model.department_id,
        )

    async def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        model = await self.user_repo.get_by_username(username)
        if not model:
            return None

        return UserEntity(
            id=model.id,
            name=model.name,
            username=model.username,
            role=model.role.value if hasattr(model.role, "value") else model.role,
            department_id=model.department_id,
        )

    async def get_user_with_embeddings(self, user_id: int) -> Optional[dict]:
        """Get user with all their face embeddings"""
        if not self.embedding_service:
            raise ValueError("Embedding service not available")

        user = await self.get_user(user_id)
        if not user:
            return None

        embeddings = await self.embedding_service.get_embeddings_by_user(user_id)

        return {
            "user": user,
            "embeddings": [
                {"id": e.id, "embedding": e.embedding[:5]}  # First 5 values only
                for e in embeddings
            ],
            "embeddings_count": len(embeddings),
        }

    async def delete_user_with_embeddings(self, user_id: int) -> bool:
        """Delete user and all their embeddings"""
        if not self.embedding_service:
            raise ValueError("Embedding service not available")

        await self.embedding_service.delete_embeddings_by_user(user_id)

        return await self.delete_user(user_id)

    async def list_users(self) -> List[UserEntity]:
        models = await self.user_repo.list()
        return [
            UserEntity(
                id=m.id,
                name=m.name,
                username=m.username,
                role=m.role.value if hasattr(m.role, "value") else m.role,
                department_id=m.department_id,
            )
            for m in models
        ]

    async def list_users_by_department(self, dept_id: int) -> List[UserEntity]:
        models = await self.user_repo.list_by_department(dept_id)
        return [
            UserEntity(
                id=m.id,
                name=m.name,
                username=m.username,
                role=m.role.value if hasattr(m.role, "value") else m.role,
                department_id=m.department_id,
            )
            for m in models
        ]

    async def list_users_by_role(self, role: str) -> List[UserEntity]:
        models = await self.user_repo.list_by_role(role)
        return [
            UserEntity(
                id=m.id,
                name=m.name,
                username=m.username,
                role=m.role.value if hasattr(m.role, "value") else m.role,
                department_id=m.department_id,
            )
            for m in models
        ]

    async def create_user(
        self,
        name: str,
        username: str,
        role: str = "employee",
        department_id: Optional[int] = None,
    ) -> UserEntity:
        existing = await self.get_user_by_username(username)
        if existing:
            raise ValueError(f"User with name '{username}' already exists")
        from app.infrastructure.db.models import UserRole

        role_enum = UserRole(role) if isinstance(role, str) else role

        model = UserModel(
            name=name, role=role_enum, department_id=department_id, username=username
        )

        created = await self.user_repo.create(model)

        return UserEntity(
            id=created.id,
            name=created.name,
            username=created.username,
            role=created.role.value if hasattr(created.role, "value") else created.role,
            department_id=created.department_id,
        )

    async def create_user_with_embedding(
        self,
        name: str,
        username: str,
        embedding: List[float],
        role: str = "employee",
        department_id: Optional[int] = None,
    ) -> UserEntity:
        """Create new user with face embedding"""
        if not self.embedding_service:
            raise ValueError("Embedding service not available")

        from app.infrastructure.db.models import UserRole

        existing = await self.get_user_by_username(username)
        if existing:
            raise ValueError(f"User with username '{username}' already exists")

        role_enum = UserRole(role) if isinstance(role, str) else role

        user_model = UserModel(
            name=name, username=username, role=role_enum, department_id=department_id
        )

        created_user = await self.user_repo.create(user_model)

        await self.embedding_service.create_embedding(
            user_id=created_user.id, embedding=embedding
        )

        return UserEntity(
            id=created_user.id,
            name=created_user.name,
            username=created_user.username,
            role=(
                created_user.role.value
                if hasattr(created_user.role, "value")
                else created_user.role
            ),
            department_id=created_user.department_id,
        )

    async def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        department_id: Optional[int] = None,
    ) -> Optional[UserEntity]:
        model = await self.user_repo.get(user_id)
        if not model:
            return None

        if name is not None:
            if name != model.name:
                existing = await self.get_user_by_name(name)
                if existing:
                    raise ValueError(f"User with name '{name}' already exists")
            model.name = name

        if role is not None:
            from app.infrastructure.db.models import UserRole

            model.role = UserRole(role)

        if department_id is not None:
            model.department_id = department_id

        updated = await self.user_repo.update(model)

        return UserEntity(
            id=updated.id,
            name=updated.name,
            username=updated.username,
            role=updated.role.value if hasattr(updated.role, "value") else updated.role,
            department_id=updated.department_id,
        )

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repo.delete(user_id)
