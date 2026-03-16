from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_auth_usecases
from app.application.usecases.auth_usecases import AuthUseCases

router = APIRouter(prefix="/auth", tags=["Auth"])



class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str



@router.post("/login", response_model=TokenResponse, summary="Login — Admin or Manager")
async def login(
    body: LoginRequest,
    usecases: AuthUseCases = Depends(get_auth_usecases),
):
    result = await usecases.login(body.username, body.password)
    return TokenResponse(**result)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh(
    body: RefreshRequest,
    usecases: AuthUseCases = Depends(get_auth_usecases),
):
    result = await usecases.refresh(body.refresh_token)
    return TokenResponse(**result)


@router.post("/logout", summary="Logout — revoke refresh token")
async def logout(
    body: LogoutRequest,
    usecases: AuthUseCases = Depends(get_auth_usecases),
):
    await usecases.logout(body.refresh_token)
    return {"detail": "Logged out successfully"}


@router.post("/logout-all", summary="Logout from all devices")
async def logout_all(
    body: LogoutRequest,
    usecases: AuthUseCases = Depends(get_auth_usecases),
):
    from app.core.dependencies import _auth_service

    token_hash = _auth_service.hash_refresh_token(body.refresh_token)
    stored = await usecases.token_repo.get_by_token_hash(token_hash)
    if stored:
        await usecases.logout_all(stored.user_id)
    return {"detail": "Logged out from all devices"}
