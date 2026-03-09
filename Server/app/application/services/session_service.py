from datetime import datetime
from uuid import uuid4, UUID
from typing import List, Optional

from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)
from app.domain.entities.session import Session
from app.infrastructure.db.models import Session as SessionModel, SessionEndReason
from app.presentation.sockets import broadcast_session_started, broadcast_session_ended


class SessionService:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    async def start_session(self, user_id: int, device_id: int) -> Session:
        existing = await self.get_active_session(user_id)
        if existing:
            await self.force_end_session(existing.id, "new_session_started")

        model = SessionModel(id=uuid4(), user_id=user_id, device_id=device_id)
        created = await self.session_repo.create(model)

        session = Session(
            id=created.id,
            user_id=created.user_id,
            device_id=created.device_id,
            login_time=created.login_time,
            logout_time=created.logout_time,
            end_reason=created.end_reason.value if created.end_reason else None,
        )

        await broadcast_session_started(
            {
                "id": str(session.id),
                "user_id": session.user_id,
                "device_id": session.device_id,
                "login_time": (
                    session.login_time.isoformat() if session.login_time else None
                ),
            }
        )

        return session

    async def end_session(self, session_id: UUID, reason: str = "logout") -> bool:
        session = await self.session_repo.get(session_id)
        if not session or session.logout_time is not None:
            return False

        session.logout_time = datetime.utcnow()
        session.end_reason = SessionEndReason(reason)

        updated = await self.session_repo.update(session)

        await broadcast_session_ended(
            {
                "id": str(session_id),
                "user_id": updated.user_id,
                "device_id": updated.device_id,
                "end_reason": reason,
                "logout_time": updated.logout_time.isoformat(),
            }
        )

        return True

    async def force_end_session(
        self, session_id: UUID, reason: str = "force_ended"
    ) -> bool:
        return await self.end_session(session_id, reason)

    async def get_session(self, session_id: UUID) -> Optional[Session]:
        model = await self.session_repo.get(session_id)
        return self._to_entity(model) if model else None

    async def get_active_session(self, user_id: int) -> Optional[Session]:
        sessions = await self.session_repo.by_user(user_id)
        for s in sessions:
            if s.logout_time is None:
                return self._to_entity(s)
        return None

    async def list_sessions(self) -> List[Session]:
        return [self._to_entity(m) for m in await self.session_repo.list()]

    async def list_active_sessions(self) -> List[Session]:
        return [self._to_entity(m) for m in await self.session_repo.list_active()]

    async def list_sessions_by_user(self, user_id: int) -> List[Session]:
        return [self._to_entity(m) for m in await self.session_repo.by_user(user_id)]

    async def list_sessions_by_device(self, device_id: int) -> List[Session]:
        return [
            self._to_entity(m) for m in await self.session_repo.by_device(device_id)
        ]

    def _to_entity(self, model) -> Session:
        return Session(
            id=model.id,
            user_id=model.user_id,
            device_id=model.device_id,
            login_time=model.login_time,
            logout_time=model.logout_time,
            end_reason=model.end_reason.value if model.end_reason else None,
        )
