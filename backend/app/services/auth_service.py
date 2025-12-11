"""Authentication and user helpers."""
from datetime import datetime, timedelta, timezone
import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from app.models import User, SubscriptionTier


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password: str, name: Optional[str] = None) -> User:
    existing = await get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=email.lower().strip(),
        password_hash=get_password_hash(password),
        name=name,
        subscription_tier=SubscriptionTier.FREE,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


def build_token_payload(user: User) -> dict:
    return {
        "sub": user.id,
        "email": user.email,
        "tier": user.subscription_tier.value if user.subscription_tier else SubscriptionTier.FREE.value,
    }


def issue_token_pair(user: User) -> dict:
    payload = build_token_payload(user)
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
    }


async def generate_verify_token(db: AsyncSession, user: User) -> str:
    user.verify_token = str(uuid.uuid4())
    await db.flush()
    return user.verify_token


async def verify_email(db: AsyncSession, token: str) -> User:
    result = await db.execute(select(User).where(User.verify_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")
    user.email_verified = True
    user.verify_token = None
    await db.flush()
    await db.refresh(user)
    return user


async def generate_reset_token(db: AsyncSession, user: User, ttl_minutes: int = 30) -> str:
    user.reset_token = str(uuid.uuid4())
    user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    await db.flush()
    return user.reset_token


async def reset_password(db: AsyncSession, token: str, new_password: str) -> User:
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
    if user.reset_token_expires_at and user.reset_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token expired")

    user.password_hash = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    await db.flush()
    await db.refresh(user)
    return user

