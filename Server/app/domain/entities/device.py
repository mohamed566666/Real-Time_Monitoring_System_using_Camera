from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Device:
    id: Optional[int]
    name: Optional[str] = None
    status: str = "offline"
    last_heartbeat: Optional[datetime] = None

    def is_online(self) -> bool:
        return self.status == "online"

    def is_locked(self) -> bool:
        return self.status == "locked"

    def lock(self):
        self.status = "locked"

    def unlock(self):
        if self.status == "locked":
            self.status = "online"

    def go_offline(self):
        self.status = "offline"

    def update_heartbeat(self):
        self.last_heartbeat = datetime.utcnow()
        self.status = "online"
