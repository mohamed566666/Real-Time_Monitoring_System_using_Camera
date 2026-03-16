from datetime import datetime
from fastapi import HTTPException, status

from app.application.services.auth_service import AuthService
from app.infrastructure.repositories.implementations.dashboard_user_repository import (
    DashboardUserRepository,
)
from app.infrastructure.repositories.implementations.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.entities.entities import RefreshTokenEntity


class AuthUseCases:

    def __init__(
        self,
        user_repo: DashboardUserRepository,
        token_repo: RefreshTokenRepository,
        auth_service: AuthService,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.auth_service = auth_service

    async def login(self, username: str, password: str) -> dict:
        user = await self.user_repo.get_by_username(username)
        if not user or not self.auth_service.verify_password(
            password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = self.auth_service.create_access_token(
            str(user.id), user.role.value
        )
        raw_refresh = self.auth_service.generate_refresh_token()
        refresh_hash = self.auth_service.hash_refresh_token(raw_refresh)

        await self.token_repo.create(
            RefreshTokenEntity(
                id=None,
                user_id=user.id,
                token_hash=refresh_hash,
                expires_at=self.auth_service.refresh_token_expires_at(),
            )
        )

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
            "role": user.role.value,
        }


    async def refresh(self, raw_refresh_token: str) -> dict:
        token_hash = self.auth_service.hash_refresh_token(raw_refresh_token)
        stored = await self.token_repo.get_by_token_hash(token_hash)

        if not stored:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if stored.expires_at < datetime.utcnow():
            await self.token_repo.delete_by_token_hash(token_hash)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
            )

        user = await self.user_repo.get_by_id(stored.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        await self.token_repo.delete_by_token_hash(token_hash)

        new_access = self.auth_service.create_access_token(
            str(user.id), user.role.value
        )
        new_raw = self.auth_service.generate_refresh_token()
        new_hash = self.auth_service.hash_refresh_token(new_raw)

        await self.token_repo.create(
            RefreshTokenEntity(
                id=None,
                user_id=user.id,
                token_hash=new_hash,
                expires_at=self.auth_service.refresh_token_expires_at(),
            )
        )

        return {
            "access_token": new_access,
            "refresh_token": new_raw,
            "token_type": "bearer",
            "role": user.role.value,
        }


    async def logout(self, raw_refresh_token: str) -> None:
        token_hash = self.auth_service.hash_refresh_token(raw_refresh_token)
        await self.token_repo.delete_by_token_hash(token_hash)


    async def logout_all(self, user_id: int) -> None:
        await self.token_repo.delete_all_by_user(user_id)
