"""Security helpers: password hashing and JWT tokens."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(data: dict, expires_minutes: int, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    minutes = expires_minutes or settings.access_token_expire_minutes
    return _create_token(data, minutes, token_type="access")


def create_refresh_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    minutes = expires_minutes or settings.refresh_token_expire_minutes
    return _create_token(data, minutes, token_type="refresh")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise exc

