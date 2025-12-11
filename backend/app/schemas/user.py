"""User and auth schemas."""
from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, EmailStr, Field

from app.models.user import SubscriptionTier


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: str
    avatar_url: Optional[str] = None
    email_verified: bool
    subscription_tier: SubscriptionTier
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class UsageCounts(BaseModel):
    mockups_generated: int
    exports: int
    brands_created: int


class UsageLimits(BaseModel):
    mockups_generated: Optional[int] = None
    exports: Optional[int] = None
    brands_created: Optional[int] = None


class UsageResponse(BaseModel):
    tier: str
    counts: Dict[str, int]
    limits: Dict[str, Optional[int]]
    resets_at: Optional[datetime]

