from uuid import UUID
from datetime import datetime

from app.presentation.sockets.socket_manager import sio
from app.presentation.sockets.socket_events import ServerEvents


async def emit_alert_to_manager(
    manager_id: int,
    alert_type: str,
    employee_id: int | None,
    session_id: UUID | None,
) -> None:
    room = f"manager_{manager_id}"
    payload = {
        "type": alert_type,
        "employee_id": employee_id,
        "session_id": str(session_id) if session_id else None,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await sio.emit(ServerEvents.ALERT, payload, room=room)


async def emit_session_closed_to_manager(
    manager_id: int,
    session_id: UUID,
    employee_id: int,
    reason: str,
) -> None:
    room = f"manager_{manager_id}"
    payload = {
        "session_id": str(session_id),
        "employee_id": employee_id,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await sio.emit(ServerEvents.SESSION_CLOSED, payload, room=room)
