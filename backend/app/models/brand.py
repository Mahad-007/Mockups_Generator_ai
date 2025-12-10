from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class Brand(Base):
    """
    Brand profile for maintaining style consistency across mockups.
    
    Stores brand DNA including colors, typography, mood, and AI-generated
    descriptions used for prompt injection.
    """
    __tablename__ = "brands"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # nullable for demo

    # Basic info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    website_url = Column(String, nullable=True)

    # Colors - stored as hex codes
    primary_color = Column(String, nullable=True)
    secondary_color = Column(String, nullable=True)
    accent_color = Column(String, nullable=True)
    background_color = Column(String, nullable=True)
    
    # Additional colors as JSON array
    color_palette = Column(JSON, nullable=True)  # ["#hex1", "#hex2", ...]

    # Typography
    primary_font = Column(String, nullable=True)
    secondary_font = Column(String, nullable=True)
    font_style = Column(String, nullable=True)  # serif, sans-serif, display, etc.

    # Style & Mood
    mood = Column(String, nullable=True)  # professional, playful, luxury, minimal, bold, etc.
    style = Column(String, nullable=True)  # modern, classic, tech, organic, vintage, etc.
    industry = Column(String, nullable=True)  # tech, beauty, food, fashion, etc.
    target_audience = Column(String, nullable=True)  # young adults, professionals, etc.

    # AI-generated prompt description for mockup generation
    prompt_description = Column(Text, nullable=True)
    
    # Suggested scene template IDs based on brand
    suggested_scenes = Column(JSON, nullable=True)  # ["scene-id-1", "scene-id-2", ...]

    # Lighting preferences based on mood
    preferred_lighting = Column(String, nullable=True)  # soft, dramatic, natural, studio
    
    # Flags
    is_default = Column(Boolean, default=False)
    is_extracted = Column(Boolean, default=False)  # True if auto-extracted from logo/website

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="brands")
    mockups = relationship("Mockup", back_populates="brand")
