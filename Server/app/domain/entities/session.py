from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID


@dataclass
class Session:
    id: UUID
    user_id: int
    device_id: int
    login_time: datetime
    logout_time: Optional[datetime] = None
    end_reason: Optional[str] = None

    def is_active(self) -> bool:
        return self.logout_time is None

    def duration_seconds(self) -> Optional[int]:
        if not self.logout_time:
            return None
        return int((self.logout_time - self.login_time).total_seconds())

    def duration_minutes(self) -> Optional[int]:
        seconds = self.duration_seconds()
        return seconds // 60 if seconds else None

    def end(self, reason: str = "logout"):
        self.logout_time = datetime.utcnow()
        self.end_reason = reason
