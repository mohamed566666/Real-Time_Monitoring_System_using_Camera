import asyncio
import logging
from datetime import datetime, timedelta

from app.infrastructure.db.database import AsyncSessionLocal
from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)
from app.infrastructure.repositories.implementations.heartbeat_repository import (
    HeartbeatRepository,
)
from app.infrastructure.repositories.implementations.employee_repository import (
    EmployeeRepository,
)
from app.infrastructure.repositories.implementations.dashboard_user_repository import (
    DashboardUserRepository,
)
from app.domain.entities.entities import SessionEndReason
from app.presentation.sockets.socket_service import emit_session_closed_to_manager

logger = logging.getLogger(__name__)

HEARTBEAT_TIMEOUT_SECONDS = 120
CHECK_INTERVAL_SECONDS = 30


async def _close_stale_sessions() -> None:
    cutoff = datetime.utcnow() - timedelta(seconds=HEARTBEAT_TIMEOUT_SECONDS)

    async with AsyncSessionLocal() as db:
        session_repo = SessionRepository(db)
        heartbeat_repo = HeartbeatRepository(db)
        employee_repo = EmployeeRepository(db)
        manager_repo = DashboardUserRepository(db)

        all_sessions = await session_repo.get_all()

        for session in all_sessions:
            if session.logout_time is not None:
                continue

            latest_hb = await heartbeat_repo.get_latest_by_session(session.id)

            reference_time = latest_hb.timestamp if latest_hb else session.login_time

            if reference_time >= cutoff:
                continue

            session.logout_time = datetime.utcnow()
            session.end_reason = SessionEndReason.GO_OFFLINE
            await session_repo.update(session)

            logger.info(
                "Auto-closed stale session %s (employee=%s, last_hb=%s)",
                session.id,
                session.employee_id,
                reference_time,
            )

            employee = await employee_repo.get_by_id(session.employee_id)
            if employee and employee.manager_id:
                await emit_session_closed_to_manager(
                    manager_id=employee.manager_id,
                    session_id=session.id,
                    employee_id=session.employee_id,
                    reason=SessionEndReason.GO_OFFLINE.value,
                )


async def run_session_timeout_worker() -> None:
    logger.info(
        "Session timeout worker started (interval=%ds, timeout=%ds)",
        CHECK_INTERVAL_SECONDS,
        HEARTBEAT_TIMEOUT_SECONDS,
    )
    while True:
        try:
            await _close_stale_sessions()
        except Exception as exc:
            logger.exception("Error in session timeout worker: %s", exc)
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
