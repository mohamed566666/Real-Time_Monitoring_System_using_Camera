class SocketEvents:
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    CONNECTED = "connected"

    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"
    SESSION_HEARTBEAT = "session_heartbeat"

    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"

    ALERT = "alert"
    NEW_ALERT = "new_alert"

    DEVICE_STATUS = "device_status"

    SUBSCRIBE_SESSION = "subscribe_session"
    UNSUBSCRIBE_SESSION = "unsubscribe_session"
    SUBSCRIBED = "subscribed"

    ERROR = "error"


class SocketRooms:
    ADMIN = "admins"
    DEVICE_PREFIX = "device:"
    SESSION_PREFIX = "session:"

    @staticmethod
    def device_room(device_id: int) -> str:
        return f"{SocketRooms.DEVICE_PREFIX}{device_id}"

    @staticmethod
    def session_room(session_id) -> str:
        return f"{SocketRooms.SESSION_PREFIX}{session_id}"
