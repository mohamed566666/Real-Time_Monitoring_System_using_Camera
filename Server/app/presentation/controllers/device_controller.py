from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field

from app.application.services.device_service import DeviceService
from app.core.dependencies import get_device_service


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(
        None, description="Device status: online, offline, locked"
    )


class DeviceStatusUpdate(BaseModel):
    status: str = Field(..., description="Device status: online, offline, locked")


class DeviceResponse(BaseModel):
    id: int
    name: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device: DeviceCreate,
    service: DeviceService = Depends(get_device_service),
):
    try:
        created = await service.create_device(name=device.name)
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    status: Optional[str] = Query(
        None, description="Filter by status: online, offline, locked"
    ),
    service: DeviceService = Depends(get_device_service),
):
    try:
        if status:
            if status not in ["online", "offline", "locked"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}. Must be online, offline, or locked",
                )
            devices = await service.list_devices_by_status(status)
        else:
            devices = await service.list_all_devices()
        return devices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    service: DeviceService = Depends(get_device_service),
):
    device = await service.get_device(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
    return device


@router.get("/by-name/{name}", response_model=DeviceResponse)
async def get_device_by_name(
    name: str,
    service: DeviceService = Depends(get_device_service),
):
    device = await service.get_device_by_name(name)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with name '{name}' not found",
        )
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    service: DeviceService = Depends(get_device_service),
):
    deleted = await service.delete_device(device_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
    return None
