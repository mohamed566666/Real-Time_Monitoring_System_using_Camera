from app.application.services.user_service import UserService
from app.application.services.face_embedding_service import FaceEmbeddingService
from app.infrastructure.aiModels.face_engine import FaceEngine
from typing import List, Optional
from app.domain.entities.user import UserEntity
import cv2
import numpy as np


class CreateUserUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(
        self,
        name: str,
        username: str,
        role: str = "employee",
        department_id: Optional[int] = None,
    ):
        try:
            return await self.service.create_user(name, username, role, department_id)
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to create user: {str(e)}")


class CreateUserWithImageUseCase:
    def __init__(self, service: UserService, face_engine: FaceEngine):
        self.service = service
        self.face_engine = face_engine

    async def execute(
        self,
        name: str,
        username: str,
        image_bytes: bytes,
        role: str = "employee",
        department_id: Optional[int] = None,
    ) -> UserEntity:
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("Invalid image file")

            face = self.face_engine.detect_face(img)
            if face is None:
                raise ValueError(
                    "No face detected in the image. Please upload a clear face image."
                )

            embedding = self.face_engine.get_embedding(face)

            return await self.service.create_user_with_embedding(
                name=name,
                username=username,
                embedding=embedding,
                role=role,
                department_id=department_id,
            )
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to create user with image: {str(e)}")


class GetUserUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> UserEntity:
        user = await self.service.get_user(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user


class GetUserByNameUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, name: str) -> UserEntity:
        user = await self.service.get_user_by_name(name)
        if not user:
            raise ValueError(f"User with name '{name}' not found")
        return user


class GetUserByUsernameUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, username: str) -> UserEntity:
        user = await self.service.get_user_by_username(username)
        if not user:
            raise ValueError(f"User with username '{username}' not found")
        return user


class GetUserWithEmbeddingsUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> dict:
        user_data = await self.service.get_user_with_embeddings(user_id)
        if not user_data:
            raise ValueError(f"User with ID {user_id} not found")
        return user_data


class UpdateUserUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(
        self,
        user_id: int,
        name: Optional[str] = None,
        role: Optional[str] = None,
        department_id: Optional[int] = None,
    ) -> UserEntity:
        updated = await self.service.update_user(
            user_id, name, None, role, department_id
        )
        if not updated:
            raise ValueError(f"User with ID {user_id} not found")
        return updated


class DeleteUserUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> bool:
        deleted = await self.service.delete_user(user_id)
        if not deleted:
            raise ValueError(f"User with ID {user_id} not found")
        return deleted


class DeleteUserWithEmbeddingsUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> bool:
        if not self.service.embedding_service:
            raise ValueError("Embedding service not available")

        deleted = await self.service.delete_user_with_embeddings(user_id)
        if not deleted:
            raise ValueError(f"User with ID {user_id} not found")
        return deleted


class ListUsersUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self) -> List[UserEntity]:
        return await self.service.list_users()


class ListUsersByRoleUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, role: str) -> List[UserEntity]:
        role_upper = role.upper()
        return await self.service.list_users_by_role(role_upper)


class ListUsersByDepartmentUseCase:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, dept_id: int) -> List[UserEntity]:
        return await self.service.list_users_by_department(dept_id)
