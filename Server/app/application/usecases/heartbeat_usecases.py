from datetime import datetime, timedelta
from uuid import UUID
from typing import List
from fastapi import HTTPException, status

from app.domain.entities.entities import HeartbeatEntity, SessionEndReason
from app.infrastructure.repositories.implementations.heartbeat_repository import (
    HeartbeatRepository,
)
from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)

HEARTBEAT_TIMEOUT_SECONDS = 90


class HeartbeatUseCases:

    def __init__(
        self, heartbeat_repo: HeartbeatRepository, session_repo: SessionRepository
    ):
        self.heartbeat_repo = heartbeat_repo
        self.session_repo = session_repo

    async def record_heartbeat(
        self, session_id: UUID, employee_id: int
    ) -> HeartbeatEntity:
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )
        if session.logout_time:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Session is already closed"
            )
        entity = HeartbeatEntity(
            id=None, session_id=session_id, employee_id=employee_id
        )
        return await self.heartbeat_repo.create(entity)

    async def check_liveness(self, session_id: UUID) -> bool:
        latest = await self.heartbeat_repo.get_latest_by_session(session_id)
        if not latest:
            return False
        cutoff = datetime.utcnow() - timedelta(seconds=HEARTBEAT_TIMEOUT_SECONDS)
        alive = latest.timestamp >= cutoff
        if not alive:
            session = await self.session_repo.get_by_id(session_id)
            if session and not session.logout_time:
                session.logout_time = datetime.utcnow()
                session.end_reason = SessionEndReason.GO_OFFLINE
                await self.session_repo.update(session)
        return alive

    async def get_session_heartbeats(self, session_id: UUID) -> List[HeartbeatEntity]:
        return await self.heartbeat_repo.get_by_session(session_id)
