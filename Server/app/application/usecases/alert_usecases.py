from app.application.services.alert_service import AlertService


class CreateAlertUseCase:
    def __init__(self, service: AlertService):
        self.service = service

    async def execute(
        self, user_id: int, device_id: int, session_id: str, alert_type: str
    ):
        return await self.service.create_alert(
            user_id, device_id, session_id, alert_type
        )


class GetSessionAlertsUseCase:
    def __init__(self, service: AlertService):
        self.service = service

    async def execute(self, session_id: str):
        return await self.service.get_alerts_by_session(session_id)


class DeleteAlertUseCase:
    def __init__(self, service: AlertService):
        self.service = service

    async def execute(self, alert_id: int):
        return await self.service.delete_alert(alert_id)


class ListAlertsByTypeUseCase:
    def __init__(self, service: AlertService):
        self.service = service

    async def execute(self, alert_type: str):
        return await self.service.list_alerts_by_type(alert_type)


class ListAllAlertsUseCase:
    def __init__(self, service: AlertService):
        self.service = service

    async def execute(self):
        return await self.service.list_alerts()


class ListAlertsByUserUseCase:
    def __init__(self, service: AlertService):
        self.service = service

    async def execute(self, user_id: int):
        all_alerts = await self.service.list_alerts()
        return [alert for alert in all_alerts if alert.user_id == user_id]
