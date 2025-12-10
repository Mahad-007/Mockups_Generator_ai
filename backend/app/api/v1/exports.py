"""Export endpoints for mockup downloads with platform optimization."""
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import io

from app.core.database import get_db
from app.core.utils import get_image_url
from app.models import Mockup
from app.services.export_service import export_service

router = APIRouter()


# Request/Response schemas
class ExportRequest(BaseModel):
    """Request for single mockup export."""
    mockup_id: str
    preset_id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: str = "png"
    quality: int = 95
    background_color: Optional[str] = None


class BatchExportRequest(BaseModel):
    """Request for batch mockup export."""
    mockup_ids: List[str]
    preset_id: Optional[str] = None
    format: str = "png"
    quality: int = 95


class MultiPresetExportRequest(BaseModel):
    """Request for exporting to multiple presets."""
    mockup_id: str
    preset_ids: List[str]


class ExportPresetInfo(BaseModel):
    """Info about a single export preset."""
    id: str
    name: str
    width: int
    height: int
    format: str


class ExportPresetsResponse(BaseModel):
    """Response with all available presets."""
    presets: dict
    categories: dict


class ExportResponse(BaseModel):
    """Response for export operations."""
    success: bool
    message: str
    download_url: Optional[str] = None
    filename: Optional[str] = None


@router.get("/presets", response_model=ExportPresetsResponse)
async def get_export_presets():
    """Get all available export presets organized by category."""
    presets = export_service.get_presets()
    categories = export_service.get_presets_by_category()

    return ExportPresetsResponse(
        presets=presets,
        categories=categories,
    )


@router.post("/single")
async def export_single(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Export a single mockup with specified settings.

    Returns the exported image directly for download.
    """
    # Get mockup from database
    result = await db.execute(select(Mockup).where(Mockup.id == request.mockup_id))
    mockup = result.scalar_one_or_none()

    if not mockup:
        raise HTTPException(status_code=404, detail="Mockup not found")

    try:
        # Export the image
        image_bytes = await export_service.export_single(
            image_path=mockup.image_path,
            preset_id=request.preset_id,
            width=request.width,
            height=request.height,
            format=request.format,
            quality=request.quality,
            background_color=request.background_color,
        )

        # Generate filename
        preset_suffix = f"_{request.preset_id}" if request.preset_id else ""
        filename = f"mockup_{mockup.id[:8]}{preset_suffix}.{request.format}"

        # Determine content type
        content_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }
        content_type = content_types.get(request.format.lower(), "image/png")

        return Response(
            content=image_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/batch")
async def export_batch(
    request: BatchExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Export multiple mockups as a ZIP file.

    Returns the ZIP file directly for download.
    """
    if not request.mockup_ids:
        raise HTTPException(status_code=400, detail="No mockup IDs provided")

    if len(request.mockup_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 mockups per batch")

    # Get mockups from database
    result = await db.execute(
        select(Mockup).where(Mockup.id.in_(request.mockup_ids))
    )
    mockups = result.scalars().all()

    if not mockups:
        raise HTTPException(status_code=404, detail="No mockups found")

    try:
        # Get image paths
        image_paths = [m.image_path for m in mockups]

        # Export to ZIP
        zip_bytes = await export_service.export_batch_to_zip(
            image_paths=image_paths,
            preset_id=request.preset_id,
            format=request.format,
            quality=request.quality,
        )

        # Generate filename
        preset_suffix = f"_{request.preset_id}" if request.preset_id else ""
        filename = f"mockups_batch{preset_suffix}.zip"

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch export failed: {str(e)}")


@router.post("/multi-preset")
async def export_multi_preset(
    request: MultiPresetExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Export a single mockup to multiple preset formats as a ZIP file.

    Useful for exporting to all social media sizes at once.
    """
    if not request.preset_ids:
        raise HTTPException(status_code=400, detail="No preset IDs provided")

    if len(request.preset_ids) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 presets per export")

    # Get mockup from database
    result = await db.execute(select(Mockup).where(Mockup.id == request.mockup_id))
    mockup = result.scalar_one_or_none()

    if not mockup:
        raise HTTPException(status_code=404, detail="Mockup not found")

    try:
        # Export to multiple presets
        zip_bytes = await export_service.export_multi_preset(
            image_path=mockup.image_path,
            preset_ids=request.preset_ids,
        )

        filename = f"mockup_{mockup.id[:8]}_all_formats.zip"

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-preset export failed: {str(e)}")


@router.get("/download/{mockup_id}")
async def download_mockup(
    mockup_id: str,
    preset_id: Optional[str] = None,
    format: str = "png",
    db: AsyncSession = Depends(get_db),
):
    """
    Quick download endpoint for a mockup.

    GET /export/download/{mockup_id}?preset_id=instagram-post&format=png
    """
    result = await db.execute(select(Mockup).where(Mockup.id == mockup_id))
    mockup = result.scalar_one_or_none()

    if not mockup:
        raise HTTPException(status_code=404, detail="Mockup not found")

    try:
        image_bytes = await export_service.export_single(
            image_path=mockup.image_path,
            preset_id=preset_id,
            format=format,
        )

        preset_suffix = f"_{preset_id}" if preset_id else ""
        filename = f"mockup_{mockup.id[:8]}{preset_suffix}.{format}"

        content_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }
        content_type = content_types.get(format.lower(), "image/png")

        return Response(
            content=image_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
