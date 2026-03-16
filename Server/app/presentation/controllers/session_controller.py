from typing import List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from app.core.dependencies import get_session_usecases, require_any_auth
from app.application.usecases.session_usecases import SessionUseCases
from app.domain.entities.entities import SessionEntity, SessionEndReason

router = APIRouter(prefix="/sessions", tags=["Sessions"])



class LoginWithEmbeddingRequest(BaseModel):
    username: str
    embedding: list[float]


class SessionClose(BaseModel):
    end_reason: SessionEndReason = SessionEndReason.LOGOUT


class SessionResponse(BaseModel):
    id: UUID
    employee_id: int
    login_time: datetime
    logout_time: Optional[datetime]
    end_reason: Optional[SessionEndReason]


def _schema(e: SessionEntity) -> SessionResponse:
    return SessionResponse(
        id=e.id,
        employee_id=e.employee_id,
        login_time=e.login_time,
        logout_time=e.logout_time,
        end_reason=e.end_reason,
    )



@router.post(
    "/open/{username}",
    response_model=SessionResponse,
    summary="[DEBUG] Open session directly by username — no face verification",
)
async def open_session_by_username(
    username: str,
    usecases: SessionUseCases = Depends(get_session_usecases),
):
    from fastapi import HTTPException

    emp = await usecases.employee_repo.get_by_username(username)
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{username}' not found")
    return _schema(await usecases.open_session(emp.id))


@router.post(
    "/login",
    response_model=SessionResponse,
    summary="Login with pre-computed embedding vector (edge device)",
)
async def login_with_embedding(
    body: LoginWithEmbeddingRequest,
    usecases: SessionUseCases = Depends(get_session_usecases),
    _: dict = Depends(require_any_auth),
):
    return _schema(await usecases.login_with_embedding(body.username, body.embedding))


@router.post(
    "/login/image",
    response_model=SessionResponse,
    summary="[DEBUG] Login with face photo — server extracts embedding",
)
async def login_with_image(
    username: str = ...,
    photo: UploadFile = File(..., description="Face photo (JPEG / PNG)"),
    usecases: SessionUseCases = Depends(get_session_usecases),
    _: dict = Depends(require_any_auth),
):
    """
    Testing convenience: send username + photo as multipart/form-data.
    Server extracts the embedding itself and opens a session if face matches.
    """
    image_bytes = await photo.read()
    return _schema(await usecases.login_with_image(username, image_bytes))



@router.post(
    "/{session_id}/close", response_model=SessionResponse, summary="Close a session"
)
async def close_session(
    session_id: UUID,
    body: SessionClose = SessionClose(),
    usecases: SessionUseCases = Depends(get_session_usecases),
    _: dict = Depends(require_any_auth),
):
    return _schema(await usecases.close_session(session_id, body.end_reason))


@router.get("", response_model=List[SessionResponse], summary="List all sessions")
async def list_all_sessions(
    usecases: SessionUseCases = Depends(get_session_usecases),
):
    return [_schema(e) for e in await usecases.list_all_sessions()]


@router.get(
    "/department/{dept_id}",
    response_model=List[SessionResponse],
    summary="List all sessions for employees in a department",
)
async def list_sessions_by_department(
    dept_id: int,
    usecases: SessionUseCases = Depends(get_session_usecases),
):
    return [_schema(e) for e in await usecases.list_sessions_by_department(dept_id)]


@router.get(
    "/employee/{employee_id}",
    response_model=List[SessionResponse],
    summary="Get all sessions for an employee",
)
async def list_sessions(
    employee_id: int,
    usecases: SessionUseCases = Depends(get_session_usecases),
    _: dict = Depends(require_any_auth),
):
    return [_schema(e) for e in await usecases.list_sessions_by_employee(employee_id)]


@router.get(
    "/employee/{employee_id}/active",
    response_model=SessionResponse,
    summary="Get active session for an employee",
)
async def get_active_session(
    employee_id: int,
    usecases: SessionUseCases = Depends(get_session_usecases),
    _: dict = Depends(require_any_auth),
):
    return _schema(await usecases.get_active_session(employee_id))


@router.get(
    "/{session_id}", response_model=SessionResponse, summary="Get session by ID"
)
async def get_session(
    session_id: UUID,
    usecases: SessionUseCases = Depends(get_session_usecases),
    _: dict = Depends(require_any_auth),
):
    return _schema(await usecases.get_session(session_id))
