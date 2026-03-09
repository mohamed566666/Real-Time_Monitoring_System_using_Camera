from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field

from app.application.usecases.device_usecases import (
    CreateDeviceUseCase,
    GetDeviceUseCase,
    ListAllDevicesUseCase,
    ListDevicesByStatusUseCase,
    DeleteDeviceUseCase,
)

from app.core.dependencies import (
    get_create_device_usecase,
    get_get_device_usecase,
    get_list_all_devices_usecase,
    get_list_devices_by_status_usecase,
    get_delete_device_usecase,
)


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


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
    use_case: CreateDeviceUseCase = Depends(get_create_device_usecase),
):
    try:
        created = await use_case.execute(name=device.name)
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
    list_all_usecase: ListAllDevicesUseCase = Depends(get_list_all_devices_usecase),
    list_by_status_usecase: ListDevicesByStatusUseCase = Depends(
        get_list_devices_by_status_usecase
    ),
):
    try:
        if status:
            devices = await list_by_status_usecase.execute(status=status)
        else:
            devices = await list_all_usecase.execute()
        return devices
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    use_case: GetDeviceUseCase = Depends(get_get_device_usecase),
):
    try:
        device = await use_case.execute(device_id=device_id)
        return device
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    use_case: DeleteDeviceUseCase = Depends(get_delete_device_usecase),
):
    try:
        await use_case.execute(device_id=device_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
