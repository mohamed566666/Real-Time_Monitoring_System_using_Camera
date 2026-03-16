import logging
from uuid import UUID

from app.presentation.sockets.socket_manager import sio
from app.presentation.sockets.socket_events import ClientEvents, ServerEvents
from app.infrastructure.db.database import AsyncSessionLocal
from app.infrastructure.repositories.implementations.heartbeat_repository import (
    HeartbeatRepository,
)
from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)
from app.domain.entities.entities import HeartbeatEntity

logger = logging.getLogger(__name__)


def register_handlers() -> None:
    @sio.event
    async def connect(sid: str, environ: dict, auth: dict | None = None):
        logger.info("Socket connected: %s", sid)

    @sio.event
    async def disconnect(sid: str):
        logger.info("Socket disconnected: %s", sid)

    @sio.on(ClientEvents.JOIN_MANAGER_ROOM)
    async def on_join_room(sid: str, data: dict):
        manager_id = data.get("manager_id")
        if not manager_id:
            return {"error": "manager_id required"}
        room = f"manager_{manager_id}"
        await sio.enter_room(sid, room)
        logger.info("sid=%s joined room %s", sid, room)
        return {"joined": room}

    @sio.on(ClientEvents.HEARTBEAT)
    async def on_heartbeat(sid: str, data: dict):
        session_id_raw = data.get("session_id")
        status = data.get("status", "")

        if not session_id_raw or status != "active":
            await sio.emit(
                ServerEvents.HEARTBEAT_ACK,
                {"ok": False, "error": "invalid payload"},
                to=sid,
            )
            return

        try:
            session_id = UUID(session_id_raw)
        except ValueError:
            await sio.emit(
                ServerEvents.HEARTBEAT_ACK,
                {"ok": False, "error": "invalid session_id format"},
                to=sid,
            )
            return

        async with AsyncSessionLocal() as db:
            session_repo = SessionRepository(db)
            heartbeat_repo = HeartbeatRepository(db)

            session = await session_repo.get_by_id(session_id)
            if not session or session.logout_time is not None:
                await sio.emit(
                    ServerEvents.HEARTBEAT_ACK,
                    {"ok": False, "error": "session not found or already closed"},
                    to=sid,
                )
                return

            heartbeat = HeartbeatEntity(
                id=None,
                session_id=session_id,
                employee_id=session.employee_id,
            )
            await heartbeat_repo.create(heartbeat)

        await sio.emit(
            ServerEvents.HEARTBEAT_ACK,
            {"ok": True, "session_id": session_id_raw},
            to=sid,
        )
        logger.debug("Heartbeat recorded for session %s", session_id_raw)
