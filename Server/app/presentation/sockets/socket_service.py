import socketio
from datetime import datetime
from uuid import UUID
from .socket_events import SocketEvents, SocketRooms
from .socket_handlers import (
    handle_connect,
    handle_disconnect,
    handle_heartbeat,
    handle_subscribe_session,
    handle_unsubscribe_session,
)

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*", 
    logger=False,
    engineio_logger=False,
)


heartbeat_service = None
session_service = None


def init_services(hb_service, sess_service):
    global heartbeat_service, session_service
    heartbeat_service = hb_service
    session_service = sess_service


@sio.event
async def connect(sid, environ, auth):
    await handle_connect(sid, environ, auth, sio)


@sio.event
async def disconnect(sid):
    await handle_disconnect(sid, sio)


@sio.event
async def heartbeat(sid, data):
    await handle_heartbeat(sid, data, sio, heartbeat_service, session_service)


@sio.event
async def subscribe_session(sid, data):
    await handle_subscribe_session(sid, data, sio)


@sio.event
async def unsubscribe_session(sid, data):
    await handle_unsubscribe_session(sid, data, sio)


async def broadcast_alert(alert_data: dict):
    payload = {**alert_data, "event": "new_alert"}
    if "session_id" in payload and payload["session_id"] is not None:
        payload["session_id"] = str(payload["session_id"])

    if "created_at" in payload and isinstance(payload["created_at"], datetime):
        payload["created_at"] = payload["created_at"].isoformat()
    
    await sio.emit(SocketEvents.ALERT, payload, room=SocketRooms.ADMIN)

    if payload.get("session_id"):
        await sio.emit(
            SocketEvents.ALERT, 
            payload, 
            room=SocketRooms.session_room(payload["session_id"])
        )
    
    print(f"[WS] Alert broadcast: type={payload.get('type')}")


async def broadcast_session_started(session_data: dict):
    payload = {**session_data, "event": "session_started"}
    if "id" in payload:
        payload["id"] = str(payload["id"])
    if "login_time" in payload and payload["login_time"]:
        if isinstance(payload["login_time"], datetime):
            payload["login_time"] = payload["login_time"].isoformat()
    
    await sio.emit(SocketEvents.SESSION_STARTED, payload, room=SocketRooms.ADMIN)
    print(f"[WS] Session started: {payload.get('id')}")


async def broadcast_session_ended(session_data: dict):
    payload = {**session_data, "event": "session_ended"}
    if "id" in payload:
        payload["id"] = str(payload["id"])
    
    session_id_str = str(session_data.get("id", ""))
    
    await sio.emit(SocketEvents.SESSION_ENDED, payload, room=SocketRooms.ADMIN)
    if session_id_str:
        await sio.emit(
            SocketEvents.SESSION_ENDED, 
            payload, 
            room=SocketRooms.session_room(session_id_str)
        )
    
    print(f"[WS] Session ended: {session_id_str} reason: {session_data.get('end_reason')}")


async def broadcast_device_status(device_id: int, status: str):
    payload = {
        "device_id": device_id,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await sio.emit(
        SocketEvents.DEVICE_STATUS,
        payload,
        room=SocketRooms.ADMIN,
    )
    print(f"[WS] Device {device_id} status: {status}")


__all__ = [
    "sio",
    "init_services",
    "broadcast_alert",
    "broadcast_session_started",
    "broadcast_session_ended",
    "broadcast_device_status",
]