from typing import List
from app.infrastructure.repositories.implementations.alert_repository import (
    AlertRepository,
)
from app.domain.entities.alert import Alert
from app.infrastructure.db.models import Alert as AlertModel, AlertType


class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    async def create_alert(
        self, user_id: int, device_id: int, session_id: str, alert_type: str
    ) -> Alert:
        model = AlertModel(
            user_id=user_id,
            device_id=device_id,
            session_id=session_id,
            type=AlertType(alert_type),
        )
        created = await self.alert_repo.create(model)
        return Alert(
            id=created.id,
            user_id=created.user_id,
            device_id=created.device_id,
            session_id=created.session_id,
            type=created.type.value,
        )

    async def get_alerts_by_session(self, session_id: str) -> List[Alert]:
        models = await self.alert_repo.by_session(session_id)
        return [
            Alert(
                id=m.id,
                user_id=m.user_id,
                device_id=m.device_id,
                session_id=m.session_id,
                type=m.type.value,
            )
            for m in models
        ]

    async def list_alerts(self) -> List[Alert]:
        models = await self.alert_repo.list()
        return [
            Alert(
                id=m.id,
                user_id=m.user_id,
                device_id=m.device_id,
                session_id=m.session_id,
                type=m.type.value,
            )
            for m in models
        ]

    async def delete_alert(self, alert_id: int) -> bool:
        return await self.alert_repo.delete(alert_id)

    async def list_alerts_by_type(self, alert_type: str) -> List[Alert]:
        models = await self.alert_repo.list_by_type(alert_type)
        return [
            Alert(
                id=m.id,
                user_id=m.user_id,
                device_id=m.device_id,
                session_id=m.session_id,
                type=m.type.value,
            )
            for m in models
        ]

    async def list_alerts_by_user(self, user_id: int) -> List[Alert]:
        models = await self.alert_repo.list_by_user(user_id)
        return [
            Alert(
                id=m.id,
                user_id=m.user_id,
                device_id=m.device_id,
                session_id=m.session_id,
                type=m.type.value,
            )
            for m in models
        ]
