from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db

from app.application.services.face_ai_service import FaceAIService
from app.application.usecases.add_employee_usecase import AddEmployeeUseCase

from app.infrastructure.repositories.implementations.heartbeat_repository import (
    HeartbeatRepository,
)
from app.application.services.heartbeat_service import HeartbeatService

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

# device use cases
from app.application.usecases.device_usecases import (
    CreateDeviceUseCase,
    GetDeviceUseCase,
    GetDeviceByNameUseCase,
    ListAllDevicesUseCase,
    ListDevicesByStatusUseCase,
    UpdateDeviceUseCase,
    UpdateDeviceStatusUseCase,
    DeleteDeviceUseCase,
)

# user use cases
from app.application.usecases.user_usecases import (
    CreateUserUseCase,
    CreateUserWithImageUseCase,
    GetUserUseCase,
    GetUserByNameUseCase,
    GetUserByUsernameUseCase,
    GetUserWithEmbeddingsUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase,
    DeleteUserWithEmbeddingsUseCase,
    ListUsersUseCase,
    ListUsersByRoleUseCase,
    ListUsersByDepartmentUseCase,
)

# session use cases
from app.application.usecases.session_usecases import (
    ListAllSessionsUseCase,
    ListActiveSessionsUseCase,
    GetSessionUseCase,
    ForceEndSessionUseCase,
    GetUserSessionHistoryUseCase,
    GetActiveSessionForUserUseCase,
)

# department use cases
from app.application.usecases.department_usecases import (
    CreateDepartmentUseCase,
    GetDepartmentUseCase,
    ListDepartmentsUseCase,
    DeleteDepartmentUseCase,
    AssignManagerUseCase,
)

# face engine
from app.infrastructure.aiModels.face_engine import FaceEngine

# websocket
from app.presentation.sockets.socket_service import sio


# ---------------- REPOSITORIES ---------------- #


def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_heartbeat_repo(db: AsyncSession = Depends(get_db)) -> HeartbeatRepository:
    return HeartbeatRepository(db)


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
    return UserService(user_repo=repo)


def get_heartbeat_service(
    heartbeat_repo: HeartbeatRepository = Depends(get_heartbeat_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
) -> HeartbeatService:
    return HeartbeatService(heartbeat_repo=heartbeat_repo, session_repo=session_repo)


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


# ---------------- WEBSOCKET ---------------- #


def get_socket_server():
    """Get Socket.IO server instance"""
    return sio


# ---------------- DEVICE USE CASES ---------------- #


def get_create_device_usecase(
    service: DeviceService = Depends(get_device_service),
) -> CreateDeviceUseCase:
    return CreateDeviceUseCase(service)


def get_get_device_usecase(
    service: DeviceService = Depends(get_device_service),
) -> GetDeviceUseCase:
    return GetDeviceUseCase(service)


def get_get_device_by_name_usecase(
    service: DeviceService = Depends(get_device_service),
) -> GetDeviceByNameUseCase:
    return GetDeviceByNameUseCase(service)


def get_list_all_devices_usecase(
    service: DeviceService = Depends(get_device_service),
) -> ListAllDevicesUseCase:
    return ListAllDevicesUseCase(service)


def get_list_devices_by_status_usecase(
    service: DeviceService = Depends(get_device_service),
) -> ListDevicesByStatusUseCase:
    return ListDevicesByStatusUseCase(service)


def get_update_device_usecase(
    service: DeviceService = Depends(get_device_service),
) -> UpdateDeviceUseCase:
    return UpdateDeviceUseCase(service)


def get_update_device_status_usecase(
    service: DeviceService = Depends(get_device_service),
) -> UpdateDeviceStatusUseCase:
    return UpdateDeviceStatusUseCase(service)


def get_delete_device_usecase(
    service: DeviceService = Depends(get_device_service),
) -> DeleteDeviceUseCase:
    return DeleteDeviceUseCase(service)


# ---------------- USER USE CASES ---------------- #


def get_create_user_usecase(
    service: UserService = Depends(get_user_service),
) -> CreateUserUseCase:
    return CreateUserUseCase(service)


def get_create_user_with_image_usecase(
    service: UserService = Depends(get_user_service_with_embedding),
    face_engine: FaceEngine = Depends(get_face_engine),
) -> CreateUserWithImageUseCase:
    return CreateUserWithImageUseCase(service, face_engine)


def get_get_user_usecase(
    service: UserService = Depends(get_user_service),
) -> GetUserUseCase:
    return GetUserUseCase(service)


def get_get_user_by_name_usecase(
    service: UserService = Depends(get_user_service),
) -> GetUserByNameUseCase:
    return GetUserByNameUseCase(service)


def get_get_user_by_username_usecase(
    service: UserService = Depends(get_user_service),
) -> GetUserByUsernameUseCase:
    return GetUserByUsernameUseCase(service)


def get_get_user_with_embeddings_usecase(
    service: UserService = Depends(get_user_service_with_embedding),
) -> GetUserWithEmbeddingsUseCase:
    return GetUserWithEmbeddingsUseCase(service)


def get_update_user_usecase(
    service: UserService = Depends(get_user_service),
) -> UpdateUserUseCase:
    return UpdateUserUseCase(service)


def get_delete_user_usecase(
    service: UserService = Depends(get_user_service),
) -> DeleteUserUseCase:
    return DeleteUserUseCase(service)


def get_delete_user_with_embeddings_usecase(
    service: UserService = Depends(get_user_service_with_embedding),
) -> DeleteUserWithEmbeddingsUseCase:
    return DeleteUserWithEmbeddingsUseCase(service)


def get_list_users_usecase(
    service: UserService = Depends(get_user_service),
) -> ListUsersUseCase:
    return ListUsersUseCase(service)


def get_list_users_by_role_usecase(
    service: UserService = Depends(get_user_service),
) -> ListUsersByRoleUseCase:
    return ListUsersByRoleUseCase(service)


def get_list_users_by_department_usecase(
    service: UserService = Depends(get_user_service),
) -> ListUsersByDepartmentUseCase:
    return ListUsersByDepartmentUseCase(service)


# ---------------- SESSION USE CASES ---------------- #


def get_list_all_sessions_usecase(
    service: SessionService = Depends(get_session_service),
) -> ListAllSessionsUseCase:
    return ListAllSessionsUseCase(service)


def get_list_active_sessions_usecase(
    service: SessionService = Depends(get_session_service),
) -> ListActiveSessionsUseCase:
    return ListActiveSessionsUseCase(service)


def get_get_session_usecase(
    service: SessionService = Depends(get_session_service),
) -> GetSessionUseCase:
    return GetSessionUseCase(service)


def get_force_end_session_usecase(
    service: SessionService = Depends(get_session_service),
) -> ForceEndSessionUseCase:
    return ForceEndSessionUseCase(service)


def get_user_session_history_usecase(
    service: SessionService = Depends(get_session_service),
) -> GetUserSessionHistoryUseCase:
    return GetUserSessionHistoryUseCase(service)


def get_active_session_for_user_usecase(
    service: SessionService = Depends(get_session_service),
) -> GetActiveSessionForUserUseCase:
    return GetActiveSessionForUserUseCase(service)


# ---------------- DEPARTMENT USE CASES ---------------- #


def get_create_department_usecase(
    service: DepartmentService = Depends(get_department_service),
) -> CreateDepartmentUseCase:
    return CreateDepartmentUseCase(service)


def get_get_department_usecase(
    service: DepartmentService = Depends(get_department_service),
) -> GetDepartmentUseCase:
    return GetDepartmentUseCase(service)


def get_list_departments_usecase(
    service: DepartmentService = Depends(get_department_service),
) -> ListDepartmentsUseCase:
    return ListDepartmentsUseCase(service)


def get_delete_department_usecase(
    service: DepartmentService = Depends(get_department_service),
) -> DeleteDepartmentUseCase:
    return DeleteDepartmentUseCase(service)


def get_assign_manager_usecase(
    service: DepartmentService = Depends(get_department_service),
) -> AssignManagerUseCase:
    return AssignManagerUseCase(service)


# ---------------- OTHER USE CASES ---------------- #


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

# Service aliases
get_face_embedding_service = get_embedding_service
get_user_service_for_controller = get_user_service
get_user_service_with_embedding_for_controller = get_user_service_with_embedding
get_department_service_for_controller = get_department_service
get_device_service_for_controller = get_device_service
get_session_service_for_controller = get_session_service
get_alert_service_for_controller = get_alert_service

# User use case aliases
get_create_user_usecase_for_controller = get_create_user_with_image_usecase
get_get_user_usecase_for_controller = get_get_user_usecase
get_get_user_by_name_usecase_for_controller = get_get_user_by_name_usecase
get_get_user_by_username_usecase_for_controller = get_get_user_by_username_usecase
get_get_user_with_embeddings_usecase_for_controller = (
    get_get_user_with_embeddings_usecase
)
get_update_user_usecase_for_controller = get_update_user_usecase
get_delete_user_usecase_for_controller = get_delete_user_usecase
get_delete_user_with_embeddings_usecase_for_controller = (
    get_delete_user_with_embeddings_usecase
)
get_list_users_usecase_for_controller = get_list_users_usecase
get_list_users_by_role_usecase_for_controller = get_list_users_by_role_usecase
get_list_users_by_department_usecase_for_controller = (
    get_list_users_by_department_usecase
)

# Device use case aliases
get_create_device_usecase_for_controller = get_create_device_usecase
get_get_device_usecase_for_controller = get_get_device_usecase
get_get_device_by_name_usecase_for_controller = get_get_device_by_name_usecase
get_list_all_devices_usecase_for_controller = get_list_all_devices_usecase
get_list_devices_by_status_usecase_for_controller = get_list_devices_by_status_usecase
get_update_device_usecase_for_controller = get_update_device_usecase
get_update_device_status_usecase_for_controller = get_update_device_status_usecase
get_delete_device_usecase_for_controller = get_delete_device_usecase

# Session use case aliases
get_list_all_sessions_usecase_for_controller = get_list_all_sessions_usecase
get_list_active_sessions_usecase_for_controller = get_list_active_sessions_usecase
get_get_session_usecase_for_controller = get_get_session_usecase
get_force_end_session_usecase_for_controller = get_force_end_session_usecase
get_user_session_history_usecase_for_controller = get_user_session_history_usecase
get_active_session_for_user_usecase_for_controller = get_active_session_for_user_usecase

# Department use case aliases
get_create_department_usecase_for_controller = get_create_department_usecase
get_get_department_usecase_for_controller = get_get_department_usecase
get_list_departments_usecase_for_controller = get_list_departments_usecase
get_delete_department_usecase_for_controller = get_delete_department_usecase
get_assign_manager_usecase_for_controller = get_assign_manager_usecase

# Other use case aliases
get_verify_user_usecase_for_controller = get_verify_user_usecase
get_verify_user_with_image_usecase_for_controller = get_verify_user_with_image_usecase
get_add_employee_usecase_for_controller = get_add_employee_usecase

# WebSocket alias
get_socket_server_for_controller = get_socket_server

get_heartbeat_service_for_controller = get_heartbeat_service
