from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class SceneTemplate(Base):
    __tablename__ = "scene_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic info
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)  # studio, lifestyle, outdoor, etc.

    # Generation
    prompt = Column(String, nullable=False)
    preview_url = Column(String, nullable=True)

    # Metadata
    tags = Column(JSON, nullable=True)  # List of tags for filtering
    customization_options = Column(JSON, nullable=True)  # Available customizations

    # Status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
