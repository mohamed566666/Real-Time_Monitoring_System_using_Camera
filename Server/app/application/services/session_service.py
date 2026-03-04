from datetime import datetime
from uuid import uuid4
from typing import Optional
from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)
from app.domain.entities.session import Session
from app.infrastructure.db.models import Session as SessionModel, SessionEndReason


class SessionService:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    async def start_session(self, user_id: int, device_id: int) -> Session:
        model = SessionModel(id=uuid4(), user_id=user_id, device_id=device_id)
        created = await self.session_repo.create(model)
        return Session(
            id=created.id,
            user_id=created.user_id,
            device_id=created.device_id,
            login_time=created.login_time,
        )

    async def end_session(self, session_id: str, reason: str) -> bool:
        return await self.session_repo.end(session_id, SessionEndReason(reason))

    async def get_active_session(self, user_id: int) -> Optional[Session]:
        sessions = await self.session_repo.by_user(user_id)
        for s in sessions:
            if s.logout_time is None:
                return Session(
                    id=s.id,
                    user_id=s.user_id,
                    device_id=s.device_id,
                    login_time=s.login_time,
                )
        return None

    async def get_session(self, session_id: str) -> Optional[Session]:
        model = await self.session_repo.get(session_id)
        if not model:
            return None
        return Session(
            id=model.id,
            user_id=model.user_id,
            device_id=model.device_id,
            login_time=model.login_time,
            logout_time=model.logout_time,
        )

    async def list_sessions(self) -> list[Session]:
        models = await self.session_repo.list()
        return [
            Session(
                id=m.id,
                user_id=m.user_id,
                device_id=m.device_id,
                login_time=m.login_time,
                logout_time=m.logout_time,
            )
            for m in models
        ]

    async def list_sessions_by_user(self, user_id: int) -> list[Session]:
        models = await self.session_repo.by_user(user_id)
        return [
            Session(
                id=m.id,
                user_id=m.user_id,
                device_id=m.device_id,
                login_time=m.login_time,
                logout_time=m.logout_time,
            )
            for m in models
        ]

    async def list_sessions_by_device(self, device_id: int) -> list[Session]:
        models = await self.session_repo.by_device(device_id)
        return [
            Session(
                id=m.id,
                user_id=m.user_id,
                device_id=m.device_id,
                login_time=m.login_time,
                logout_time=m.logout_time,
            )
            for m in models
        ]
