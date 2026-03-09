# websocket_interactive.py
import asyncio
import socketio
from datetime import datetime
import json
import sys

sio = socketio.AsyncClient()
current_role = None


@sio.event
async def connect():
    print(f"\n✅ Connected as {current_role}")
    print(f"   SID: {sio.sid}")


@sio.event
async def disconnect():
    print("\n❌ Disconnected")


@sio.event
async def connected(data):
    print(f"\n📡 Connection acknowledged: {data}")


@sio.event
async def alert(data):
    print(f"\n🚨 ALERT: {json.dumps(data, indent=2)}")


@sio.event
async def session_started(data):
    print(f"\n🎯 SESSION STARTED: {json.dumps(data, indent=2)}")


@sio.event
async def session_ended(data):
    print(f"\n🏁 SESSION ENDED: {json.dumps(data, indent=2)}")


@sio.event
async def device_status(data):
    print(f"\n💻 DEVICE STATUS: {json.dumps(data, indent=2)}")


@sio.event
async def session_heartbeat(data):
    print(f"\n❤️ HEARTBEAT: {json.dumps(data, indent=2)}")


@sio.event
async def heartbeat_ack(data):
    print(f"\n✅ HEARTBEAT ACK: {data}")


@sio.event
async def subscribed(data):
    print(f"\n📋 SUBSCRIBED: {data}")


@sio.event
async def error(data):
    print(f"\n❌ ERROR: {data}")


async def menu():
    """Interactive menu"""
    while True:
        print("\n" + "=" * 50)
        print("WebSocket Interactive Test")
        print("=" * 50)
        print("1. Connect as Device")
        print("2. Connect as Admin")
        print("3. Send Heartbeat")
        print("4. Subscribe to Session")
        print("5. Unsubscribe from Session")
        print("6. Disconnect")
        print("7. Exit")
        print("=" * 50)

        choice = input("Enter choice (1-7): ").strip()

        if choice == "1":
            await connect_device()
        elif choice == "2":
            await connect_admin()
        elif choice == "3":
            await send_heartbeat()
        elif choice == "4":
            await subscribe_session()
        elif choice == "5":
            await unsubscribe_session()
        elif choice == "6":
            await disconnect()
        elif choice == "7":
            if sio.connected:
                await sio.disconnect()
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice!")

        await asyncio.sleep(1)


async def connect_device():
    """Connect as device"""
    global current_role
    if sio.connected:
        await sio.disconnect()

    device_id = input("Enter device ID (default: 123): ").strip()
    device_id = int(device_id) if device_id else 123

    current_role = f"device_{device_id}"
    await sio.connect(
        "http://localhost:8000",
        socketio_path="ws",
        auth={"role": "device", "device_id": device_id},
    )


async def connect_admin():
    """Connect as admin"""
    global current_role
    if sio.connected:
        await sio.disconnect()

    current_role = "admin"
    await sio.connect(
        "http://localhost:8000", socketio_path="ws", auth={"role": "admin"}
    )


async def send_heartbeat():
    """Send heartbeat"""
    if not sio.connected:
        print("Not connected!")
        return

    session_id = input("Enter session ID (default: test-session-123): ").strip()
    session_id = session_id or "test-session-123"

    device_id = input("Enter device ID (default: 123): ").strip()
    device_id = int(device_id) if device_id else 123

    user_id = input("Enter user ID (default: 456): ").strip()
    user_id = int(user_id) if user_id else 456

    await sio.emit(
        "heartbeat",
        {
            "session_id": session_id,
            "device_id": device_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
    print("Heartbeat sent!")


async def subscribe_session():
    """Subscribe to session"""
    if not sio.connected:
        print("Not connected!")
        return

    session_id = input("Enter session ID: ").strip()
    if not session_id:
        print("Session ID required!")
        return

    await sio.emit("subscribe_session", {"session_id": session_id})
    print(f"Subscription request sent for session {session_id}")


async def unsubscribe_session():
    """Unsubscribe from session"""
    if not sio.connected:
        print("Not connected!")
        return

    session_id = input("Enter session ID: ").strip()
    if not session_id:
        print("Session ID required!")
        return

    await sio.emit("unsubscribe_session", {"session_id": session_id})
    print(f"Unsubscription request sent for session {session_id}")


async def disconnect():
    """Disconnect"""
    if sio.connected:
        await sio.disconnect()
        print("Disconnected!")
    else:
        print("Already disconnected!")


async def main():
    """Main function"""
    try:
        await menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted!")
    finally:
        if sio.connected:
            await sio.disconnect()


if __name__ == "__main__":
    print("=" * 50)
    print("WebSocket Interactive Test Client")
    print("=" * 50)
    print("Make sure server is running on http://localhost:8000")
    print("=" * 50)

    asyncio.run(main())
