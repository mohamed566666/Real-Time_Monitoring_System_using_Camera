from datetime import datetime, timedelta
from typing import List, Optional, Dict
from uuid import UUID
from app.infrastructure.repositories.implementations.heartbeat_repository import (
    HeartbeatRepository,
)
from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)
from app.presentation.sockets import broadcast_session_ended


class HeartbeatService:
    def __init__(
        self, heartbeat_repo: HeartbeatRepository, session_repo: SessionRepository
    ):
        self.heartbeat_repo = heartbeat_repo
        self.session_repo = session_repo

    async def record_heartbeat(self, session_id: UUID) -> Dict:

        session = await self.session_repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.logout_time is not None:
            raise ValueError(f"Session {session_id} is already ended")

        heartbeat = await self.heartbeat_repo.create_heartbeat(
            session_id=session_id, device_id=session.device_id, user_id=session.user_id
        )

        return {
            "id": heartbeat.id,
            "session_id": str(heartbeat.session_id),
            "device_id": heartbeat.device_id,
            "user_id": heartbeat.user_id,
            "timestamp": heartbeat.timestamp.isoformat(),
        }

    async def get_last_heartbeat(self, session_id: UUID) -> Optional[Dict]:
        heartbeat = await self.heartbeat_repo.get_last_heartbeat(session_id)
        if not heartbeat:
            return None

        return {
            "session_id": str(heartbeat.session_id),
            "device_id": heartbeat.device_id,
            "user_id": heartbeat.user_id,
            "timestamp": heartbeat.timestamp.isoformat(),
            "seconds_ago": (datetime.utcnow() - heartbeat.timestamp).total_seconds(),
        }

    async def check_stale_sessions(self, minutes: int = 2) -> List[UUID]:
        stale_session_ids = await self.heartbeat_repo.get_sessions_without_heartbeat(
            minutes
        )

        ended_sessions = []
        for session_id in stale_session_ids:
            session = await self.session_repo.get(session_id)
            if session and session.logout_time is None:

                session.logout_time = datetime.utcnow()
                session.end_reason = "heartbeat_timeout"
                await self.session_repo.update(session)

                await broadcast_session_ended(
                    {
                        "id": str(session_id),
                        "user_id": session.user_id,
                        "device_id": session.device_id,
                        "end_reason": "heartbeat_timeout",
                        "logout_time": session.logout_time.isoformat(),
                    }
                )

                ended_sessions.append(session_id)
                print(
                    f"[Heartbeat] Session {session_id} ended - no heartbeat for {minutes} minutes"
                )

        return ended_sessions

    async def get_session_heartbeat_status(self, session_id: UUID) -> Dict:
        session = await self.session_repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        last_hb = await self.get_last_heartbeat(session_id)

        return {
            "session_id": str(session_id),
            "user_id": session.user_id,
            "device_id": session.device_id,
            "is_active": session.logout_time is None,
            "login_time": (
                session.login_time.isoformat() if session.login_time else None
            ),
            "last_heartbeat": last_hb,
            "status": (
                "healthy"
                if last_hb and last_hb["seconds_ago"] < 120
                else "stale" if session.logout_time is None else "ended"
            ),
        }
