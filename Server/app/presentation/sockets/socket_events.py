class ClientEvents:
    HEARTBEAT = "heartbeat"
    JOIN_MANAGER_ROOM = "join_room"


class ServerEvents:
    HEARTBEAT_ACK = "heartbeat_ack"
    ALERT = "alert"
    SESSION_CLOSED = "session_closed"
