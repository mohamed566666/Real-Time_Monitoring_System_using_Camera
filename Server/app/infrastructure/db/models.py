# app/infrastructure/db/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime
import uuid
import enum

from app.infrastructure.db.base import Base


class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class SessionEndReason(enum.Enum):
    LOGOUT = "logout"
    LOCK = "lock"
    ERROR = "error"


class AlertType(enum.Enum):
    NO_FACE = "no-face"
    MATCH_FAILED = "match_failed"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SYSTEM_ERROR = "system_error"


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    manager_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_departments_manager_id", use_alter=True),
        nullable=True,
    )
    members = relationship(
        "User", back_populates="department", foreign_keys="[User.department_id]"
    )
    manager = relationship(
        "User", foreign_keys=[manager_id], back_populates="managed_department"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE)
    department_id = Column(
        Integer,
        ForeignKey("departments.id", name="fk_users_department_id"),
        nullable=True,
    )

    department = relationship(
        "Department", back_populates="members", foreign_keys=[department_id]
    )
    managed_department = relationship(
        "Department", foreign_keys="[Department.manager_id]", back_populates="manager"
    )
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    face_embeddings = relationship(
        "FaceEmbedding", back_populates="user", cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="user")


Department.manager = relationship(
    "User", foreign_keys=[Department.manager_id], back_populates="managed_department"
)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    status = Column(String(30), default="offline")

    sessions = relationship(
        "Session", back_populates="device", cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="device")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    login_time = Column(DateTime, default=datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)
    end_reason = Column(Enum(SessionEndReason), nullable=True)

    user = relationship("User", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")
    alerts = relationship("Alert", back_populates="session")


class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)

    user = relationship("User", back_populates="face_embeddings")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    type = Column(Enum(AlertType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")
    device = relationship("Device", back_populates="alerts")
    session = relationship("Session", back_populates="alerts")
