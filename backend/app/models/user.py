from sqlalchemy import Column, String, DateTime, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.models.base import Base


class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"
    AGENCY = "agency"


class TeamRole(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


def _default_usage():
    """Default usage counters per user."""
    return {
        "mockups_generated": 0,
        "exports": 0,
        "brands_created": 0,
    }


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column("hashed_password", String, nullable=True)  # Keep column name for compatibility
    name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    stripe_customer_id = Column(String, nullable=True)

    # Usage tracking
    usage_counts = Column(JSON, default=_default_usage)
    usage_reset_at = Column(DateTime, nullable=True)

    # OAuth (future expansion)
    google_id = Column(String, nullable=True, unique=True)
    github_id = Column(String, nullable=True, unique=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

    # Security tokens (dev-friendly stubs)
    verify_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan")
    mockups = relationship("Mockup", back_populates="user", cascade="all, delete-orphan")
    brands = relationship("Brand", back_populates="user", cascade="all, delete-orphan")
    teams_owned = relationship("Team", back_populates="owner", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMembership", back_populates="user", cascade="all, delete-orphan")
