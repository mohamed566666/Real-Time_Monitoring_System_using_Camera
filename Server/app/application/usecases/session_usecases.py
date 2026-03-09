from app.application.services.session_service import SessionService
from app.domain.entities.session import Session
from typing import List, Optional
from uuid import UUID


class ListAllSessionsUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self) -> List[Session]:
        return await self.service.list_sessions()


class ListActiveSessionsUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self) -> List[Session]:
        return await self.service.list_active_sessions()


class GetSessionUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, session_id: UUID) -> Optional[Session]:
        session = await self.service.get_session(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found")
        return session


class ForceEndSessionUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, session_id: UUID, reason: str = "force_ended") -> bool:
        success = await self.service.force_end_session(session_id, reason)
        if not success:
            raise ValueError(f"Session with ID {session_id} not found or already ended")
        return success


class GetUserSessionHistoryUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, user_id: int) -> List[Session]:
        return await self.service.list_sessions_by_user(user_id)


class GetActiveSessionForUserUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, user_id: int) -> Optional[Session]:
        session = await self.service.get_active_session(user_id)
        if not session:
            raise ValueError(f"No active session found for user {user_id}")
        return session
