import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


class AuthService:

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

    @staticmethod
    def create_access_token(
        subject: str, role: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return jwt.encode(
            {"sub": subject, "role": role, "exp": expire, "type": "access"},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(64)

    @staticmethod
    def hash_refresh_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    @staticmethod
    def refresh_token_expires_at() -> datetime:
        return datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
