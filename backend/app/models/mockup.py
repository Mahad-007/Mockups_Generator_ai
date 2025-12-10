"""Mockup model - stores generated mockup images."""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Mockup(Base):
    __tablename__ = "mockups"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)

    # Generated image path
    image_path = Column(String, nullable=False)

    # Generation details
    scene_template_id = Column(String, nullable=True)
    prompt_used = Column(String, nullable=True)
    generation_params = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="mockups")
