from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import AsyncSessionLocal
from app.infrastructure.aiModels.face_engine import FaceEngine
from app.core.config import settings
from app.application.services.auth_service import AuthService

from app.infrastructure.repositories.implementations.dashboard_user_repository import (
    DashboardUserRepository,
)
from app.infrastructure.repositories.implementations.admin_repository import (
    AdminRepository,
)
from app.infrastructure.repositories.implementations.manager_repository import (
    ManagerRepository,
)
from app.infrastructure.repositories.implementations.department_repository import (
    DepartmentRepository,
)
from app.infrastructure.repositories.implementations.employee_repository import (
    EmployeeRepository,
)
from app.infrastructure.repositories.implementations.face_embedding_repository import (
    FaceEmbeddingRepository,
)
from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)
from app.infrastructure.repositories.implementations.heartbeat_repository import (
    HeartbeatRepository,
)
from app.infrastructure.repositories.implementations.alert_repository import (
    AlertRepository,
)
from app.infrastructure.repositories.implementations.refresh_token_repository import (
    RefreshTokenRepository,
)

from app.application.usecases.auth_usecases import AuthUseCases
from app.application.usecases.admin_usecases import AdminUseCases
from app.application.usecases.manager_usecases import ManagerUseCases
from app.application.usecases.department_usecases import DepartmentUseCases
from app.application.usecases.employee_usecases import EmployeeUseCases
from app.application.usecases.session_usecases import SessionUseCases
from app.application.usecases.heartbeat_usecases import HeartbeatUseCases
from app.application.usecases.face_embedding_usecases import FaceEmbeddingUseCases


# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------

_auth_service = AuthService()
_face_engine = FaceEngine(recognition_threshold=settings.FACE_RECOGNITION_THRESHOLD)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ---------------------------------------------------------------------------
# DB session
# ---------------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------------------------------------------------------
# Repository factories
# ---------------------------------------------------------------------------


def get_dashboard_user_repo(
    db: AsyncSession = Depends(get_db),
) -> DashboardUserRepository:
    return DashboardUserRepository(db)


def get_admin_repo(db: AsyncSession = Depends(get_db)) -> AdminRepository:
    return AdminRepository(db)


def get_manager_repo(db: AsyncSession = Depends(get_db)) -> ManagerRepository:
    return ManagerRepository(db)


def get_dept_repo(db: AsyncSession = Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(db)


def get_employee_repo(db: AsyncSession = Depends(get_db)) -> EmployeeRepository:
    return EmployeeRepository(db)


def get_embedding_repo(db: AsyncSession = Depends(get_db)) -> FaceEmbeddingRepository:
    return FaceEmbeddingRepository(db)


def get_session_repo(db: AsyncSession = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)


def get_heartbeat_repo(db: AsyncSession = Depends(get_db)) -> HeartbeatRepository:
    return HeartbeatRepository(db)


def get_alert_repo(db: AsyncSession = Depends(get_db)) -> AlertRepository:
    return AlertRepository(db)


def get_refresh_token_repo(
    db: AsyncSession = Depends(get_db),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


# ---------------------------------------------------------------------------
# Use-case factories
# ---------------------------------------------------------------------------


def get_auth_usecases(
    user_repo: DashboardUserRepository = Depends(get_dashboard_user_repo),
    token_repo: RefreshTokenRepository = Depends(get_refresh_token_repo),
) -> AuthUseCases:
    return AuthUseCases(user_repo, token_repo, _auth_service)


def get_admin_usecases(
    admin_repo: AdminRepository = Depends(get_admin_repo),
) -> AdminUseCases:
    return AdminUseCases(admin_repo, _auth_service)


def get_manager_usecases(
    manager_repo: ManagerRepository = Depends(get_manager_repo),
    dept_repo: DepartmentRepository = Depends(get_dept_repo),
) -> ManagerUseCases:
    return ManagerUseCases(manager_repo, dept_repo, _auth_service)


def get_dept_usecases(
    dept_repo: DepartmentRepository = Depends(get_dept_repo),
) -> DepartmentUseCases:
    return DepartmentUseCases(dept_repo)


def get_employee_usecases(
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
    manager_repo: ManagerRepository = Depends(get_manager_repo),
    dept_repo: DepartmentRepository = Depends(get_dept_repo),
) -> EmployeeUseCases:
    return EmployeeUseCases(employee_repo, manager_repo, dept_repo)


def get_session_usecases(
    session_repo: SessionRepository = Depends(get_session_repo),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
    embedding_repo: FaceEmbeddingRepository = Depends(get_embedding_repo),
) -> SessionUseCases:
    return SessionUseCases(session_repo, employee_repo, embedding_repo, _face_engine)


def get_heartbeat_usecases(
    heartbeat_repo: HeartbeatRepository = Depends(get_heartbeat_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
) -> HeartbeatUseCases:
    return HeartbeatUseCases(heartbeat_repo, session_repo)


def get_face_embedding_usecases(
    embedding_repo: FaceEmbeddingRepository = Depends(get_embedding_repo),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
) -> FaceEmbeddingUseCases:
    return FaceEmbeddingUseCases(embedding_repo, employee_repo, _face_engine)


# ---------------------------------------------------------------------------
# Auth guards — DISABLED for development, no token needed
# To enable: swap with the JWT implementation below
# ---------------------------------------------------------------------------


async def require_admin() -> dict:
    return {"role": "admin", "sub": "1"}


async def require_manager() -> dict:
    return {"role": "manager", "sub": "1"}


async def require_any_auth() -> dict:
    return {"role": "admin", "sub": "1"}


# ---------------------------------------------------------------------------
# JWT implementation — uncomment when ready for production
# ---------------------------------------------------------------------------
# async def _get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
#     try:
#         return _auth_service.decode_token(token)
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid or expired token",
#                             headers={"WWW-Authenticate": "Bearer"})
#
# async def require_admin(identity: dict = Depends(_get_current_user)) -> dict:
#     if identity.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Admin access required")
#     return identity
#
# async def require_manager(identity: dict = Depends(_get_current_user)) -> dict:
#     if identity.get("role") not in ("admin", "manager"):
#         raise HTTPException(status_code=403, detail="Manager access required")
#     return identity
#
# async def require_any_auth(identity: dict = Depends(_get_current_user)) -> dict:
#     return identity
