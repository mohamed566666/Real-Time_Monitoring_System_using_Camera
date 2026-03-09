from typing import List, Optional
from datetime import datetime
from app.infrastructure.repositories.implementations.device_repository import (
    DeviceRepository,
)
from app.domain.entities.device import Device as DeviceEntity
from app.infrastructure.db.models import Device as DeviceModel


class DeviceService:
    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo

    async def _broadcast_status(self, device_id: int, status: str):
        from app.presentation.sockets.socket_service import broadcast_device_status

        await broadcast_device_status(device_id, status)

    async def get_device(self, device_id: int) -> Optional[DeviceEntity]:
        model = await self.device_repo.get(device_id)
        if not model:
            return None
        return DeviceEntity(id=model.id, name=model.name, status=model.status)

    async def get_device_by_name(self, name: str) -> Optional[DeviceEntity]:
        model = await self.device_repo.get_by_name(name)
        if not model:
            return None
        return DeviceEntity(id=model.id, name=model.name, status=model.status)

    async def list_all_devices(self) -> List[DeviceEntity]:
        models = await self.device_repo.list_all()
        return [DeviceEntity(id=m.id, name=m.name, status=m.status) for m in models]

    async def list_online_devices(self) -> List[DeviceEntity]:
        models = await self.device_repo.list_online()
        return [DeviceEntity(id=m.id, name=m.name, status=m.status) for m in models]

    async def list_offline_devices(self) -> List[DeviceEntity]:
        models = await self.device_repo.list_offline()
        return [DeviceEntity(id=m.id, name=m.name, status=m.status) for m in models]

    async def list_locked_devices(self) -> List[DeviceEntity]:
        models = await self.device_repo.list_locked()
        return [DeviceEntity(id=m.id, name=m.name, status=m.status) for m in models]

    async def list_devices_by_status(self, status: str) -> List[DeviceEntity]:
        models = await self.device_repo.list_by_status(status)
        return [DeviceEntity(id=m.id, name=m.name, status=m.status) for m in models]

    async def create_device(self, name: str) -> DeviceEntity:
        model = DeviceModel(name=name, status="offline")
        created = await self.device_repo.create(model)
        return DeviceEntity(id=created.id, name=created.name, status=created.status)

    async def update_device(
        self, device_id: int, name: Optional[str] = None, status: Optional[str] = None
    ) -> Optional[DeviceEntity]:
        model = await self.device_repo.get(device_id)
        if not model:
            return None

        old_status = model.status

        if name is not None:
            model.name = name

        if status is not None:
            if status in ["online", "offline", "locked"]:
                model.status = status

        updated = await self.device_repo.update(model)

        if status is not None and old_status != status:
            await self._broadcast_status(device_id, status)

        return DeviceEntity(id=updated.id, name=updated.name, status=updated.status)

    async def update_device_status(
        self, device_id: int, status: str
    ) -> Optional[DeviceEntity]:
        if status not in ["online", "offline", "locked"]:
            raise ValueError(f"Invalid status: {status}")

        updated = await self.device_repo.update_status(device_id, status)
        if not updated:
            return None

        await self._broadcast_status(device_id, status)

        return DeviceEntity(id=updated.id, name=updated.name, status=updated.status)

    async def delete_device(self, device_id: int) -> bool:
        await self._broadcast_status(device_id, "deleted")
        return await self.device_repo.delete(device_id)

    async def get_last_heartbeat(self, device_id: int) -> Optional[datetime]:
        """Get last heartbeat time for device"""
        # يمكنك تنفيذ هذه الدالة إذا كان عندك جدول للـ heartbeats
        pass
