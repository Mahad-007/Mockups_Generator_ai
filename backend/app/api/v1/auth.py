"""Authentication endpoints (credentials-only, email flows stubbed)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel, EmailStr

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.services import auth_service
from app.services.auth_service import issue_token_pair
from app.schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    AuthResponse,
)
from app.utils.rate_limiter import rate_limit

router = APIRouter()


class RefreshRequest(BaseModel):
    refresh_token: str


class VerificationRequest(BaseModel):
    token: str


class ResetRequest(BaseModel):
    email: EmailStr


class ResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/register", response_model=AuthResponse)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    rate_limit(f"register:{payload.email}", limit=5, window_seconds=60)
    user = await auth_service.create_user(db, payload.email, payload.password, name=payload.name)
    tokens = issue_token_pair(user)
    return AuthResponse(user=user, tokens=TokenResponse(**tokens))


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    rate_limit(f"login:{payload.email}", limit=10, window_seconds=60)
    user = await auth_service.authenticate_user(db, payload.email, payload.password)
    tokens = issue_token_pair(user)
    return AuthResponse(user=user, tokens=TokenResponse(**tokens))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
):
    from jose import JWTError
    from app.core.security import decode_token, create_access_token, create_refresh_token
    try:
        payload = decode_token(request.refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    # Issue new pair
    user_claims = {k: v for k, v in payload.items() if k in {"sub", "email", "tier"}}
    return TokenResponse(
        access_token=create_access_token(user_claims),
        refresh_token=create_refresh_token(user_claims),
        token_type="bearer",
    )


@router.post("/logout")
async def logout():
    # Stateless JWT - nothing to revoke yet
    return {"message": "Logged out"}


@router.post("/request-verification")
async def request_verification(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    token = await auth_service.generate_verify_token(db, current_user)
    return {
        "message": "Verification email not sent (stubbed for development).",
        "verification_token": token,
    }


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(
    payload: VerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.verify_email(db, payload.token)
    tokens = issue_token_pair(user)
    return AuthResponse(user=user, tokens=TokenResponse(**tokens))


@router.post("/request-reset")
async def request_reset(
    payload: ResetRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.get_user_by_email(db, payload.email)
    if not user:
        # Do not reveal user existence
        return {"message": "If the account exists, a reset token was generated."}
    token = await auth_service.generate_reset_token(db, user)
    return {
        "message": "Password reset email not sent (stubbed for development).",
        "reset_token": token,
    }


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(
    payload: ResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.reset_password(db, payload.token, payload.new_password)
    tokens = issue_token_pair(user)
    return AuthResponse(user=user, tokens=TokenResponse(**tokens))

