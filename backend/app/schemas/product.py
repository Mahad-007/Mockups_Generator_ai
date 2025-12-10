"""Product schemas."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema."""
    category: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class ProductCreate(ProductBase):
    """Schema for creating a product (internal use)."""
    original_image_path: str
    processed_image_path: Optional[str] = None


class ProductResponse(ProductBase):
    """Schema for product API response."""
    id: str
    original_image_url: str
    processed_image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
