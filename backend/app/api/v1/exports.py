from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class ExportRequest(BaseModel):
    mockup_id: str
    preset: Optional[str] = None  # instagram-post, amazon-main, etc.
    width: Optional[int] = None
    height: Optional[int] = None
    format: str = "png"  # png, jpg, webp
    quality: int = 90


class BatchExportRequest(BaseModel):
    mockup_ids: List[str]
    preset: Optional[str] = None
    format: str = "png"
    quality: int = 90


# Platform presets
EXPORT_PRESETS = {
    "instagram-post": {"width": 1080, "height": 1080, "name": "Instagram Post"},
    "instagram-story": {"width": 1080, "height": 1920, "name": "Instagram Story"},
    "amazon-main": {"width": 1000, "height": 1000, "name": "Amazon Main Image"},
    "amazon-lifestyle": {"width": 1500, "height": 1500, "name": "Amazon Lifestyle"},
    "website-hero": {"width": 1920, "height": 1080, "name": "Website Hero"},
    "facebook-ad": {"width": 1200, "height": 628, "name": "Facebook Ad"},
    "pinterest": {"width": 1000, "height": 1500, "name": "Pinterest"},
}


@router.get("/presets")
async def get_export_presets():
    """Get available export presets for different platforms."""
    return {"presets": EXPORT_PRESETS}


@router.post("/single")
async def export_single(request: ExportRequest):
    """Export a single mockup with specified settings."""
    # TODO: Implement export
    # 1. Get mockup from database
    # 2. Apply preset or custom dimensions
    # 3. Resize and optimize
    # 4. Return download URL

    return {
        "message": "Export started",
        "mockup_id": request.mockup_id,
        "format": request.format,
        "download_url": None,  # Will be populated when ready
    }


@router.post("/batch")
async def export_batch(request: BatchExportRequest):
    """Export multiple mockups as a zip file."""
    # TODO: Implement batch export
    # 1. Process each mockup
    # 2. Create zip archive
    # 3. Return download URL

    return {
        "message": "Batch export started",
        "mockup_count": len(request.mockup_ids),
        "download_url": None,  # Will be populated when ready
    }
