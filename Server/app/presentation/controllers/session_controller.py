from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import List, Optional

from app.core.dependencies import (
    get_list_all_sessions_usecase_for_controller,
    get_list_active_sessions_usecase_for_controller,
    get_get_session_usecase_for_controller,
    get_force_end_session_usecase_for_controller,
    get_user_session_history_usecase_for_controller,
    get_active_session_for_user_usecase_for_controller,
)
from app.application.usecases.session_usecases import (
    ListAllSessionsUseCase,
    ListActiveSessionsUseCase,
    GetSessionUseCase,
    ForceEndSessionUseCase,
    GetUserSessionHistoryUseCase,
    GetActiveSessionForUserUseCase,
)
from app.domain.entities.session import Session

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/")
async def get_all_sessions(
    usecase: ListAllSessionsUseCase = Depends(
        get_list_all_sessions_usecase_for_controller
    ),
) -> List[Session]:
    """Get all sessions (both active and ended)"""
    return await usecase.execute()


@router.get("/active")
async def get_active_sessions(
    usecase: ListActiveSessionsUseCase = Depends(
        get_list_active_sessions_usecase_for_controller
    ),
) -> List[Session]:
    """List currently active sessions (not logged out)"""
    return await usecase.execute()


@router.get("/user/{user_id}")
async def get_user_session_history(
    user_id: int,
    usecase: GetUserSessionHistoryUseCase = Depends(
        get_user_session_history_usecase_for_controller
    ),
) -> List[Session]:
    """Get session history for a specific user"""
    return await usecase.execute(user_id)


@router.get("/user/{user_id}/active")
async def get_user_active_session(
    user_id: int,
    usecase: GetActiveSessionForUserUseCase = Depends(
        get_active_session_for_user_usecase_for_controller
    ),
):
    """Get active session for a specific user (if any)"""
    session = await usecase.execute(user_id)
    if not session:
        raise HTTPException(
            status_code=404, detail="No active session found for this user"
        )
    return session


@router.get("/{session_id}")
async def get_session(
    session_id: UUID,
    usecase: GetSessionUseCase = Depends(get_get_session_usecase_for_controller),
) -> Session:
    """Get session by ID"""
    session = await usecase.execute(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/{session_id}/force-end")
async def force_end_session(
    session_id: UUID,
    usecase: ForceEndSessionUseCase = Depends(
        get_force_end_session_usecase_for_controller
    ),
):
    """Force-end a session (admin only maybe)"""
    success = await usecase.execute(session_id, "force_ended")
    if not success:
        raise HTTPException(
            status_code=404, detail="Session not found or already ended"
        )
    return {"message": "Session ended successfully", "session_id": str(session_id)}
