from datetime import datetime
from uuid import UUID
from .socket_events import SocketEvents, SocketRooms


async def handle_connect(sid, environ, auth, sio):
    role = (auth or {}).get("role", "unknown")
    device_id = (auth or {}).get("device_id")

    if role == "admin":
        await sio.enter_room(sid, SocketRooms.ADMIN)
        print(f"[WS] Admin connected: {sid}")
    elif role == "device" and device_id is not None:
        room = SocketRooms.device_room(device_id)
        await sio.enter_room(sid, room)
        print(f"[WS] Device {device_id} connected: {sid}")
    else:
        print(f"[WS] Unknown connection: {sid} with role {role}")

    await sio.emit(
        SocketEvents.CONNECTED,
        {"status": "ok", "sid": sid, "role": role},
        to=sid,
    )


async def handle_disconnect(sid, sio):
    print(f"[WS] Client disconnected: {sid}")


async def handle_heartbeat(sid, data, sio, heartbeat_service, session_service):
    session_id = data.get("session_id")
    ts = data.get("timestamp") or datetime.utcnow().isoformat()

    if not session_id:
        await sio.emit(
            SocketEvents.ERROR,
            {"message": "heartbeat requires session_id"},
            to=sid,
        )
        return

    try:
        session = await session_service.get_session(UUID(session_id))
        if not session:
            await sio.emit(
                SocketEvents.ERROR,
                {"message": f"Session {session_id} not found"},
                to=sid,
            )
            return

        if hasattr(session, 'logout_time') and session.logout_time:
            await sio.emit(
                SocketEvents.ERROR,
                {"message": f"Session {session_id} has already ended"},
                to=sid,
            )
            return

        heartbeat_data = await heartbeat_service.record_heartbeat(
            session_id=UUID(session_id)
        )
        
        payload = {
            "session_id": str(session_id),
            "device_id": session.device_id,
            "user_id": session.user_id,
            "timestamp": ts,
            "heartbeat_id": heartbeat_data["id"],
            "type": "heartbeat",
        }

        await sio.emit(
            SocketEvents.HEARTBEAT_ACK,
            {
                "session_id": str(session_id),
                "timestamp": ts,
                "heartbeat_id": heartbeat_data["id"]
            },
            to=sid,
        )

        await sio.emit(
            SocketEvents.SESSION_HEARTBEAT, 
            payload, 
            room=SocketRooms.ADMIN
        )

        print(f"[WS] Heartbeat recorded for session {session_id}")

    except ValueError as e:
        await sio.emit(
            SocketEvents.ERROR,
            {"message": str(e)},
            to=sid,
        )
    except Exception as e:
        await sio.emit(
            SocketEvents.ERROR,
            {"message": f"Internal error: {str(e)}"},
            to=sid,
        )


async def handle_subscribe_session(sid, data, sio):
    session_id = data.get("session_id")
    if session_id:
        await sio.enter_room(sid, SocketRooms.session_room(session_id))
        await sio.emit(
            SocketEvents.SUBSCRIBED, 
            {"session_id": str(session_id)}, 
            to=sid
        )
        print(f"[WS] Client {sid} subscribed to session {session_id}")


async def handle_unsubscribe_session(sid, data, sio):
    session_id = data.get("session_id")
    if session_id:
        await sio.leave_room(sid, SocketRooms.session_room(session_id))
        print(f"[WS] Client {sid} unsubscribed from session {session_id}")