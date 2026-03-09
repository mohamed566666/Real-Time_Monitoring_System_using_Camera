# app/infrastructure/repositories/interfaces/device_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from app.infrastructure.db.models import Device


class IDeviceRepository(ABC):

    @abstractmethod
    async def get(self, id: int) -> Optional[Device]:
        """Get device by ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Device]:
        """Get device by name"""
        pass

    @abstractmethod
    async def list_all(self) -> List[Device]:
        """List all devices"""
        pass

    @abstractmethod
    async def list_online(self) -> List[Device]:
        """List online devices"""
        pass

    @abstractmethod
    async def list_offline(self) -> List[Device]:
        """List offline devices"""
        pass

    @abstractmethod
    async def list_by_status(self, status: str) -> List[Device]:
        """List devices by status"""
        pass

    @abstractmethod
    async def create(self, device: Device) -> Device:
        """Create new device"""
        pass

    @abstractmethod
    async def update(self, device: Device) -> Device:
        """Update device"""
        pass

    @abstractmethod
    async def update_status(self, device_id: int, status: str) -> Optional[Device]:
        """Update device status"""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Delete device by ID"""
        pass
