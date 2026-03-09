from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Get auth data from query params
    role = websocket.query_params.get("role", "unknown")
    device_id = websocket.query_params.get("device_id")

    print(f"[WS] Client connected - Role: {role}, Device: {device_id}")

    try:
        # Send connected message
        await websocket.send_json({"event": "connected", "status": "ok", "role": role})

        # Handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            event = message.get("event")

            if event == "heartbeat":
                session_id = message.get("session_id")
                await websocket.send_json(
                    {
                        "event": "heartbeat_ack",
                        "session_id": session_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                print(f"[WS] Heartbeat from session {session_id}")

            elif event == "subscribe_session":
                session_id = message.get("session_id")
                await websocket.send_json(
                    {"event": "subscribed", "session_id": session_id}
                )

    except WebSocketDisconnect:
        print(f"[WS] Client disconnected")
    except Exception as e:
        print(f"[WS] Error: {e}")
