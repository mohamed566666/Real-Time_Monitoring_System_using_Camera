from typing import List, Optional
from datetime import datetime
from app.infrastructure.repositories.implementations.alert_repository import (
    AlertRepository,
)
from app.domain.entities.alert import Alert
from app.infrastructure.db.models import Alert as AlertModel, AlertType


class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    @staticmethod
    async def _broadcast(alert_data: dict):
        from app.presentation.sockets.socket_service import broadcast_alert

        await broadcast_alert(alert_data)

    async def create_alert(
        self,
        user_id: int,
        device_id: int,
        session_id: str,
        alert_type: str,
    ) -> Alert:
        model = AlertModel(
            user_id=user_id,
            device_id=device_id,
            session_id=session_id,
            type=AlertType(alert_type),
            created_at=datetime.utcnow(),
        )
        created = await self.alert_repo.create(model)

        alert = Alert(
            id=created.id,
            user_id=created.user_id,
            device_id=created.device_id,
            session_id=str(created.session_id) if created.session_id else None,
            type=created.type.value,
            created_at=created.created_at,
        )

        await self._broadcast(
            {
                "id": alert.id,
                "type": alert.type,
                "user_id": alert.user_id,
                "device_id": alert.device_id,
                "session_id": alert.session_id,
                "created_at": (
                    alert.created_at.isoformat() if alert.created_at else None
                ),
            }
        )

        return alert

    async def delete_alert(self, alert_id: int) -> bool:
        return await self.alert_repo.delete(alert_id)

    async def get_alerts_by_session(self, session_id: str) -> List[Alert]:
        models = await self.alert_repo.by_session(session_id)
        return [self._to_entity(m) for m in models]

    async def list_alerts(self) -> List[Alert]:
        models = await self.alert_repo.list()
        return [self._to_entity(m) for m in models]

    async def list_alerts_by_type(self, alert_type: str) -> List[Alert]:
        models = await self.alert_repo.list_by_type(alert_type)
        return [self._to_entity(m) for m in models]

    async def list_alerts_by_user(self, user_id: int) -> List[Alert]:
        models = await self.alert_repo.list_by_user(user_id)
        return [self._to_entity(m) for m in models]

    async def list_alerts_by_device(self, device_id: int) -> List[Alert]:
        models = await self.alert_repo.list_by_device(device_id)
        return [self._to_entity(m) for m in models]

    async def list_alerts_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Alert]:
        models = await self.alert_repo.list_by_date_range(start_date, end_date)
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_entity(m) -> Alert:
        return Alert(
            id=m.id,
            user_id=m.user_id,
            device_id=m.device_id,
            session_id=str(m.session_id) if m.session_id else None,
            type=m.type.value,
            created_at=m.created_at,
        )
