"""Product model - stores uploaded product images."""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Image paths (local storage for MVP)
    original_image_path = Column(String, nullable=False)
    processed_image_path = Column(String, nullable=True)  # Background removed

    # AI-detected metadata
    category = Column(String, nullable=True)
    attributes = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    mockups = relationship("Mockup", back_populates="product", cascade="all, delete-orphan")
    user = relationship("User", back_populates="products")
