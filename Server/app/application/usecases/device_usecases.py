from app.application.services.device_service import DeviceService
from app.domain.entities.device import Device
from typing import List, Optional


class CreateDeviceUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, name: str) -> Device:
        return await self.service.create_device(name)


class GetDeviceUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, device_id: int) -> Optional[Device]:
        device = await self.service.get_device(device_id)
        if not device:
            raise ValueError(f"Device with ID {device_id} not found")
        return device


class GetDeviceByNameUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, name: str) -> Optional[Device]:
        device = await self.service.get_device_by_name(name)
        if not device:
            raise ValueError(f"Device with name '{name}' not found")
        return device


class ListAllDevicesUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self) -> List[Device]:
        return await self.service.list_all_devices()


class ListDevicesByStatusUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, status: str) -> List[Device]:
        if status not in ["online", "offline", "locked"]:
            raise ValueError(
                f"Invalid status: {status}. Must be online, offline, or locked"
            )
        return await self.service.list_devices_by_status(status)


class UpdateDeviceUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(
        self, device_id: int, name: Optional[str] = None, status: Optional[str] = None
    ) -> Optional[Device]:
        if status and status not in ["online", "offline", "locked"]:
            raise ValueError(
                f"Invalid status: {status}. Must be online, offline, or locked"
            )

        device = await self.service.update_device(device_id, name, status)
        if not device:
            raise ValueError(f"Device with ID {device_id} not found")
        return device


class UpdateDeviceStatusUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, device_id: int, status: str) -> Optional[Device]:
        if status not in ["online", "offline", "locked"]:
            raise ValueError(
                f"Invalid status: {status}. Must be online, offline, or locked"
            )

        device = await self.service.update_device_status(device_id, status)
        if not device:
            raise ValueError(f"Device with ID {device_id} not found")
        return device


class DeleteDeviceUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, device_id: int) -> bool:
        deleted = await self.service.delete_device(device_id)
        if not deleted:
            raise ValueError(f"Device with ID {device_id} not found")
        return deleted
