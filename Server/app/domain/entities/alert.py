from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Alert:
    id: Optional[int]
    type: str
    user_id: Optional[int] = None
    device_id: Optional[int] = None
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)