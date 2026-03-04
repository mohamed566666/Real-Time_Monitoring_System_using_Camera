from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db

from app.application.services.face_ai_service import FaceAIService
from app.application.usecases.add_employee_usecase import AddEmployeeUseCase

# repositories
from app.infrastructure.repositories.implementations.user_repository import (
    UserRepository,
)
from app.infrastructure.repositories.implementations.device_repository import (
    DeviceRepository,
)
from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)
from app.infrastructure.repositories.implementations.department_repository import (
    DepartmentRepository,
)
from app.infrastructure.repositories.implementations.alert_repository import (
    AlertRepository,
)
from app.infrastructure.repositories.implementations.face_embedding_repository import (
    FaceEmbeddingRepository,
)

from app.application.usecases.auth_use_cases import (
    VerifyUserIdentityUseCase,
    VerifyUserWithImageUseCase,
)

# services
from app.application.services.user_service import UserService
from app.application.services.device_service import DeviceService
from app.application.services.session_service import SessionService
from app.application.services.department_service import DepartmentService
from app.application.services.alert_service import AlertService
from app.application.services.face_embedding_service import FaceEmbeddingService

# face engine
from app.infrastructure.aiModels.face_engine import FaceEngine


# ---------------- REPOSITORIES ---------------- #


def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_device_repo(db: AsyncSession = Depends(get_db)) -> DeviceRepository:
    return DeviceRepository(db)


def get_session_repo(db: AsyncSession = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)


def get_department_repo(db: AsyncSession = Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(db)


def get_alert_repo(db: AsyncSession = Depends(get_db)) -> AlertRepository:
    return AlertRepository(db)


def get_embedding_repo(db: AsyncSession = Depends(get_db)) -> FaceEmbeddingRepository:
    return FaceEmbeddingRepository(db)


# ---------------- SERVICES ---------------- #


def get_user_service(repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo=repo)  # بدون embedding service


def get_embedding_service(
    repo: FaceEmbeddingRepository = Depends(get_embedding_repo),
) -> FaceEmbeddingService:
    """Get face embedding service with repository"""
    return FaceEmbeddingService(repo)


def get_user_service_with_embedding(
    user_repo: UserRepository = Depends(get_user_repo),
    embedding_service: FaceEmbeddingService = Depends(get_embedding_service),
) -> UserService:
    """User service with embedding support"""
    return UserService(user_repo=user_repo, embedding_service=embedding_service)


def get_device_service(
    repo: DeviceRepository = Depends(get_device_repo),
) -> DeviceService:
    return DeviceService(repo)


def get_session_service(
    repo: SessionRepository = Depends(get_session_repo),
) -> SessionService:
    return SessionService(repo)


def get_department_service(
    repo: DepartmentRepository = Depends(get_department_repo),
) -> DepartmentService:
    return DepartmentService(repo)


def get_alert_service(repo: AlertRepository = Depends(get_alert_repo)) -> AlertService:
    return AlertService(repo)


def get_face_ai_service() -> FaceAIService:
    """FaceAI service doesn't need repo, it's just AI logic"""
    return FaceAIService()


# ---------------- FACE ENGINE ---------------- #

_face_engine_instance = None


def get_face_engine() -> FaceEngine:
    """Get FaceEngine instance (singleton)"""
    global _face_engine_instance
    if _face_engine_instance is None:
        _face_engine_instance = FaceEngine()
    return _face_engine_instance


# ---------------- USE CASES ---------------- #


def get_add_employee_usecase(
    user_service: UserService = Depends(get_user_service_with_embedding),
    embedding_service: FaceEmbeddingService = Depends(get_embedding_service),
    ai_service: FaceAIService = Depends(get_face_ai_service),
) -> AddEmployeeUseCase:
    return AddEmployeeUseCase(
        user_service=user_service,
        embedding_service=embedding_service,
        ai_service=ai_service,
    )


def get_verify_user_usecase(
    user_service: UserService = Depends(get_user_service_with_embedding),
    embedding_service: FaceEmbeddingService = Depends(get_embedding_service),
    face_engine: FaceEngine = Depends(get_face_engine),
) -> VerifyUserIdentityUseCase:
    """Get verify user identity use case"""
    return VerifyUserIdentityUseCase(
        user_service=user_service,
        embedding_service=embedding_service,
        face_engine=face_engine,
        similarity_threshold=0.6,
    )


def get_verify_user_with_image_usecase(
    verify_usecase: VerifyUserIdentityUseCase = Depends(get_verify_user_usecase),
    face_engine: FaceEngine = Depends(get_face_engine),
) -> VerifyUserWithImageUseCase:
    """Get verify user with image use case"""
    return VerifyUserWithImageUseCase(
        verify_usecase=verify_usecase, face_engine=face_engine
    )


# ---------------- FOR CONTROLLERS ---------------- #

# Aliases for controllers
get_face_embedding_service = get_embedding_service
get_user_service_for_controller = get_user_service
get_user_service_with_embedding_for_controller = get_user_service_with_embedding
get_department_service_for_controller = get_department_service
get_device_service_for_controller = get_device_service
get_session_service_for_controller = get_session_service
get_alert_service_for_controller = get_alert_service
get_verify_user_usecase_for_controller = get_verify_user_usecase
get_verify_user_with_image_usecase_for_controller = get_verify_user_with_image_usecase
