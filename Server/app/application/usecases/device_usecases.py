from app.application.services.device_service import DeviceService


class CreateDeviceUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, name: str):
        return await self.service.create_device(name)


class ChangeDeviceStatusUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, device_id: int, status: str):
        if status not in ["online", "offline"]:
            raise ValueError("Invalid status")

        device = await self.service.update_status(device_id, status)
        if not device:
            raise ValueError("Device not found")

        return device


class DeleteDeviceUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, device_id: int):
        return await self.service.delete_device(device_id)


class ListOnlineDevicesUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self):
        return await self.service.list_online_devices()


class ListAllDevicesUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self):
        return await self.service.list_all_devices()


class GetDeviceUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, device_id: int):
        device = await self.service.get_device(device_id)
        if not device:
            raise ValueError("Device not found")
        return device


class ListDevicesByStatusUseCase:
    def __init__(self, service: DeviceService):
        self.service = service

    async def execute(self, status: str):
        if status not in ["online", "offline"]:
            raise ValueError("Invalid status")
        all_devices = await self.service.list_all_devices()
        return [d for d in all_devices if d.status == status]
