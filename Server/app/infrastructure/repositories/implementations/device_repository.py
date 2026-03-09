from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.infrastructure.db.models import Device as DeviceModel
from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.interfaces.device_repository import (
    IDeviceRepository,
)


class DeviceRepository(BaseRepository[DeviceModel], IDeviceRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, DeviceModel)

    async def get(self, id: int) -> Optional[DeviceModel]:
        return await self.get_by_id(id)

    async def get_by_name(self, name: str) -> Optional[DeviceModel]:
        return await self.get_by_field("name", name)

    async def list_all(self) -> List[DeviceModel]:
        return await self.get_all()

    async def list_online(self) -> List[DeviceModel]:
        return await self.filter(status="online")

    async def list_offline(self) -> List[DeviceModel]:
        return await self.filter(status="offline")

    async def list_by_status(self, status: str) -> List[DeviceModel]:
        return await self.filter(status=status)

    async def create(self, device: DeviceModel) -> DeviceModel:
        try:
            if device.name:
                existing = await self.get_by_name(device.name)
                if existing:
                    raise ValueError(f"Device with name '{device.name}' already exists")

            return await self.add(device)
        except Exception as e:
            raise e

    async def update(self, device: DeviceModel) -> DeviceModel:
        try:
            existing = await self.get_by_id(device.id)
            if existing and existing.name != device.name and device.name:
                name_check = await self.get_by_name(device.name)
                if name_check:
                    raise ValueError(f"Device with name '{device.name}' already exists")

            return await super().update(device)
        except Exception as e:
            raise e

    async def update_status(self, device_id: int, status: str) -> Optional[DeviceModel]:
        try:
            device = await self.get_by_id(device_id)
            if not device:
                return None

            device.status = status
            return await self.update(device)
        except Exception as e:
            raise e

    async def delete(self, device_id: int) -> bool:
        return await self.delete_by_id(device_id)
