"""Mockup schemas."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class MockupGenerateRequest(BaseModel):
    """Request schema for generating a mockup."""
    product_id: str
    scene_template_id: Optional[str] = "studio-white"
    custom_prompt: Optional[str] = None


class MockupResponse(BaseModel):
    """Schema for mockup API response."""
    id: str
    product_id: str
    image_url: str
    scene_template_id: Optional[str] = None
    prompt_used: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GenerationStatus(BaseModel):
    """Schema for generation status response."""
    status: str  # processing, completed, failed
    message: str
    mockup: Optional[MockupResponse] = None
