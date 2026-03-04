from app.infrastructure.db.models import Alert
from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.interfaces.alert_repository import IAlertRepository


class AlertRepository(BaseRepository[Alert], IAlertRepository):

    def __init__(self, session):
        super().__init__(session, Alert)

    async def create(self, alert):
        return await self.add(alert)

    async def by_session(self, session_id):
        return await self.filter(session_id=session_id)
