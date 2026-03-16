from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
import enum

from app.infrastructure.db.base import Base




class DashboardRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"


class SessionEndReason(enum.Enum):
    LOGOUT = "logout"
    LOCK = "lock"
    ERROR = "error"
    GO_OFFLINE = "go_offline"


class AlertType(enum.Enum):
    NO_FACE = "no-face"
    MATCH_FAILED = "match_failed"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SYSTEM_ERROR = "system_error"



class DashboardUser(Base):
    __tablename__ = "dashboard_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(DashboardRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": None,
    }



class Admin(DashboardUser):
    __tablename__ = "admins"

    id = Column(
        Integer, ForeignKey("dashboard_users.id", ondelete="CASCADE"), primary_key=True
    )

    __mapper_args__ = {
        "polymorphic_identity": DashboardRole.ADMIN,
    }




class Manager(DashboardUser):
    __tablename__ = "managers"

    id = Column(
        Integer, ForeignKey("dashboard_users.id", ondelete="CASCADE"), primary_key=True
    )
    department_id = Column(
        Integer,
        ForeignKey(
            "departments.id", ondelete="SET NULL", name="fk_managers_department_id"
        ),
        nullable=True,
    )

    department = relationship("Department", back_populates="manager")

    __mapper_args__ = {
        "polymorphic_identity": DashboardRole.MANAGER,
    }



class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    manager = relationship("Manager", back_populates="department", uselist=False)
    employees = relationship("Employee", back_populates="department")



class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    worked_hours = Column(Float, default=0.0, nullable=False)
    is_online = Column(
        Boolean, default=False, nullable=False
    ) 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    department_id = Column(
        Integer,
        ForeignKey(
            "departments.id", ondelete="SET NULL", name="fk_employees_department_id"
        ),
        nullable=True,
    )

    department = relationship("Department", back_populates="employees")
    face_embedding = relationship(
        "FaceEmbedding",
        back_populates="employee",
        uselist=False,
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "Session", back_populates="employee", cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="employee")



class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer,
        ForeignKey(
            "employees.id", ondelete="CASCADE", name="fk_face_embeddings_employee_id"
        ),
        unique=True,
        nullable=False,
    )
    embedding = Column(ARRAY(Float), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="face_embedding")



class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE", name="fk_sessions_employee_id"),
        nullable=False,
    )
    login_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    logout_time = Column(DateTime, nullable=True)
    end_reason = Column(Enum(SessionEndReason), nullable=True)

    employee = relationship("Employee", back_populates="sessions")
    heartbeats = relationship(
        "DeviceHeartbeat", back_populates="session", cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="session")



class DeviceHeartbeat(Base):
    __tablename__ = "device_heartbeats"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE", name="fk_heartbeats_session_id"),
        nullable=False,
    )
    employee_id = Column(
        Integer,
        ForeignKey(
            "employees.id", ondelete="CASCADE", name="fk_heartbeats_employee_id"
        ),
        nullable=False,
    )
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    session = relationship("Session", back_populates="heartbeats")
    employee = relationship("Employee")



class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL", name="fk_alerts_employee_id"),
        nullable=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE", name="fk_alerts_session_id"),
        nullable=True,
    )
    type = Column(Enum(AlertType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="alerts")
    session = relationship("Session", back_populates="alerts")




class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey(
            "dashboard_users.id", ondelete="CASCADE", name="fk_refresh_tokens_user_id"
        ),
        nullable=False,
        index=True,
    )
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("DashboardUser")
