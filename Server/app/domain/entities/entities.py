from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import enum


class DashboardRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"


class SessionEndReason(str, enum.Enum):
    LOGOUT = "logout"
    LOCK = "lock"
    ERROR = "error"
    GO_OFFLINE = "go_offline"


class AlertType(str, enum.Enum):
    NO_FACE = "no-face"
    MATCH_FAILED = "match_failed"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SYSTEM_ERROR = "system_error"


@dataclass
class DashboardUserEntity:
    id: Optional[int]
    username: str
    hashed_password: str
    role: DashboardRole
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdminEntity(DashboardUserEntity):

    pass


@dataclass
class ManagerEntity(DashboardUserEntity):
    department_id: Optional[int] = None


@dataclass
class DepartmentEntity:
    id: Optional[int]
    name: str


@dataclass
class EmployeeEntity:
    id: Optional[int]
    name: str
    username: str
    department_id: Optional[int]
    worked_hours: float = 8.0
    is_online: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FaceEmbeddingEntity:
    id: Optional[int]
    employee_id: int
    embedding: List[float]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SessionEntity:
    id: Optional[UUID]
    employee_id: int
    login_time: datetime = field(default_factory=datetime.utcnow)
    logout_time: Optional[datetime] = None
    end_reason: Optional[SessionEndReason] = None


@dataclass
class HeartbeatEntity:
    id: Optional[int]
    session_id: UUID
    employee_id: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertEntity:
    id: Optional[int]
    type: AlertType
    session_id: Optional[UUID] = None
    employee_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RefreshTokenEntity:
    id: Optional[int]
    user_id: int
    token_hash: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
