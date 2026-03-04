from fastapi import Depends
from app.infrastructure.db.database import get_db
from .implementations.user_repository import UserRepository
from .implementations.session_repository import SessionRepository
from .implementations.device_repository import DeviceRepository
from .implementations.department_repository import DepartmentRepository
from .implementations.alert_repository import AlertRepository
from .implementations.face_embedding_repository import FaceEmbeddingRepository


async def get_user_repo(session=Depends(get_db)):
    return UserRepository(session)


async def get_session_repo(session=Depends(get_db)):
    return SessionRepository(session)


async def get_device_repo(session=Depends(get_db)):
    return DeviceRepository(session)


async def get_department_repo(session=Depends(get_db)):
    return DepartmentRepository(session)


async def get_alert_repo(session=Depends(get_db)):
    return AlertRepository(session)


async def get_embedding_repo(session=Depends(get_db)):
    return FaceEmbeddingRepository(session)