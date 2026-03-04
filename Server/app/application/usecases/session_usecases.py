from app.application.services.session_service import SessionService


class StartSessionUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, user_id: int, device_id: int):
        active = await self.service.get_active_session(user_id)
        if active:
            raise ValueError("User already has active session")

        return await self.service.start_session(user_id, device_id)


class EndSessionUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, session_id: str, reason: str):
        success = await self.service.end_session(session_id, reason)
        if not success:
            raise ValueError("Session not found or already ended")
        return True


class GetUserActiveSessionUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, user_id: int):
        return await self.service.get_active_session(user_id)


class GetSessionUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, session_id: str):
        session = await self.service.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        return session


class ListSessionsUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self):
        return await self.service.list_sessions()


class ListSessionsByUserUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, user_id: int):
        return await self.service.list_sessions_by_user(user_id)


class ListSessionsByDeviceUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self, device_id: int):
        return await self.service.list_sessions_by_device(device_id)


class ListActiveSessionsUseCase:
    def __init__(self, service: SessionService):
        self.service = service

    async def execute(self):
        sessions = await self.service.list_sessions()
        return [s for s in sessions if s.logout_time is None]
