from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.models.base import Base


class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"
    AGENCY = "agency"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)  # Null for OAuth users
    name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    stripe_customer_id = Column(String, nullable=True)

    # Usage tracking
    mockups_generated_this_month = Column(Integer, default=0)
    usage_reset_date = Column(DateTime, nullable=True)

    # OAuth
    google_id = Column(String, nullable=True, unique=True)
    github_id = Column(String, nullable=True, unique=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan")
    mockups = relationship("Mockup", back_populates="user", cascade="all, delete-orphan")
    brands = relationship("Brand", back_populates="user", cascade="all, delete-orphan")
