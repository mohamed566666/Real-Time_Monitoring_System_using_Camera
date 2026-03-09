# test_websocket.py
import asyncio
import socketio
from datetime import datetime
import json

# Socket.IO client
sio = socketio.AsyncClient()


@sio.event
async def connect():
    print("✅ Connected to WebSocket server")
    print(f"   SID: {sio.sid}")


@sio.event
async def disconnect():
    print("❌ Disconnected from WebSocket server")


@sio.event
async def connected(data):
    print(f"📡 Connection acknowledged: {data}")


@sio.event
async def alert(data):
    print(f"🚨 Alert received: {json.dumps(data, indent=2)}")


@sio.event
async def session_started(data):
    print(f"🎯 Session started: {json.dumps(data, indent=2)}")


@sio.event
async def session_ended(data):
    print(f"🏁 Session ended: {json.dumps(data, indent=2)}")


@sio.event
async def device_status(data):
    print(f"💻 Device status: {json.dumps(data, indent=2)}")


@sio.event
async def session_heartbeat(data):
    print(f"❤️ Heartbeat: {json.dumps(data, indent=2)}")


@sio.event
async def heartbeat_ack(data):
    print(f"✅ Heartbeat ACK: {data}")


@sio.event
async def subscribed(data):
    print(f"📋 Subscribed: {data}")


@sio.event
async def error(data):
    print(f"❌ Error: {data}")


async def test_device():
    """Test as a device"""
    print("\n🔧 Testing as DEVICE...")

    # Connect as device
    await sio.connect(
        "http://localhost:8000",
        socketio_path="ws",
        auth={"role": "device", "device_id": 123},
    )

    await asyncio.sleep(1)

    # Send heartbeat
    print("\n💓 Sending heartbeat...")
    await sio.emit(
        "heartbeat",
        {
            "session_id": "test-session-123",
            "device_id": 123,
            "user_id": 456,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    await asyncio.sleep(2)

    # Subscribe to session
    print("\n🔔 Subscribing to session...")
    await sio.emit("subscribe_session", {"session_id": "test-session-123"})

    await asyncio.sleep(2)

    await sio.disconnect()


async def test_admin():
    """Test as an admin"""
    print("\n👑 Testing as ADMIN...")

    # Connect as admin
    await sio.connect(
        "http://localhost:8000", socketio_path="ws", auth={"role": "admin"}
    )

    await asyncio.sleep(5)  # Listen for events

    await sio.disconnect()


async def test_all():
    """Run all tests"""
    try:
        # Test device
        await test_device()

        await asyncio.sleep(2)

        # Test admin
        await test_admin()

    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        if sio.connected:
            await sio.disconnect()


if __name__ == "__main__":
    print("=" * 50)
    print("WebSocket Test Client")
    print("=" * 50)
    print("Make sure server is running on http://localhost:8000")
    print("=" * 50)

    asyncio.run(test_all())
