"""Batch generation endpoints for creating multiple mockup variations."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.utils import get_image_url
from app.core.batch_queue import batch_queue, JobStatus
from app.models import Mockup
from app.services.batch_service import batch_service, VARIATION_PRESETS

router = APIRouter()


# Request/Response schemas
class VariationCustomization(BaseModel):
    """Customization for a single variation."""
    template_id: str
    customization: Optional[Dict[str, str]] = None


class BatchGenerateRequest(BaseModel):
    """Request for batch mockup generation."""
    product_id: str
    scene_template_ids: Optional[List[str]] = None
    variation_preset: str = Field(
        default="standard",
        description="One of: quick, standard, comprehensive"
    )
    max_variations: int = Field(default=10, ge=1, le=20)
    custom_variations: Optional[List[VariationCustomization]] = None


class JobStatusResponse(BaseModel):
    """Response for job status queries."""
    id: str
    job_type: str
    status: str
    total_items: int
    completed_items: int
    failed_items: int
    progress: float
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    results: List[Dict[str, Any]] = []


class BatchGenerateResponse(BaseModel):
    """Response for batch generation initiation."""
    job_id: str
    status: str
    total_variations: int
    message: str


class MockupVariation(BaseModel):
    """A single mockup variation result."""
    id: str
    image_url: str
    scene_template_id: Optional[str] = None
    customization: Optional[Dict[str, str]] = None


class BatchResultResponse(BaseModel):
    """Response with completed batch results."""
    job_id: str
    status: str
    mockups: List[MockupVariation]
    failed_count: int


class VariationPresetsResponse(BaseModel):
    """Available variation presets."""
    presets: Dict[str, Dict[str, Any]]


@router.post("/generate", response_model=BatchGenerateResponse)
async def start_batch_generation(
    request: BatchGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Start batch mockup generation with variations.

    Creates multiple mockup variations in parallel with progress tracking.
    Returns a job ID that can be polled for status.

    Variation presets:
    - quick: 2-3 variations, fast generation
    - standard: 5-6 variations, balanced coverage
    - comprehensive: 10+ variations, full coverage
    """
    # Convert custom variations if provided
    custom_vars = None
    if request.custom_variations:
        custom_vars = [
            {
                "template_id": v.template_id,
                "customization": v.customization or {},
            }
            for v in request.custom_variations
        ]

    try:
        job = await batch_service.start_batch_generation(
            db=db,
            product_id=request.product_id,
            scene_template_ids=request.scene_template_ids,
            variation_preset=request.variation_preset,
            max_variations=request.max_variations,
            custom_variations=custom_vars,
        )

        return BatchGenerateResponse(
            job_id=job.id,
            status=job.status.value,
            total_variations=job.total_items,
            message="Batch generation started. Poll /batch/status/{job_id} for progress.",
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch: {str(e)}")


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a batch generation job.

    Poll this endpoint to track progress.
    When status is 'completed', results are available.
    """
    status = batch_service.get_job_status(job_id)

    if not status:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(**status)


@router.post("/status/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running batch generation job."""
    success = await batch_service.cancel_job(job_id)

    if not success:
        raise HTTPException(status_code=400, detail="Could not cancel job (may already be completed)")

    return {"message": "Job cancelled", "job_id": job_id}


@router.get("/results/{job_id}", response_model=BatchResultResponse)
async def get_batch_results(
    job_id: str,
    save_to_db: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    Get results of a completed batch job.

    Set save_to_db=true to persist mockups to database (default).
    Can only be called once job status is 'completed'.
    """
    job = batch_queue.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.is_done:
        raise HTTPException(
            status_code=400,
            detail=f"Job not complete. Status: {job.status.value}, Progress: {job.progress:.1f}%"
        )

    # Get successful results
    successful_results = [r for r in job.results if r.success and r.result]

    # Save to database if requested and job has product_id
    mockups = []
    if save_to_db and successful_results and job.metadata.get("product_id"):
        mockups = await batch_service.save_completed_mockups(
            db=db,
            job=job,
            product_id=job.metadata["product_id"],
        )

    # Build response
    mockup_variations = []
    for i, result in enumerate(successful_results):
        data = result.result
        mockup_id = mockups[i].id if i < len(mockups) else f"temp_{i}"
        mockup_variations.append(MockupVariation(
            id=mockup_id,
            image_url=get_image_url(data["image_path"]),
            scene_template_id=data.get("scene_template_id"),
            customization=data.get("customization"),
        ))

    return BatchResultResponse(
        job_id=job_id,
        status=job.status.value,
        mockups=mockup_variations,
        failed_count=job.failed_items,
    )


@router.get("/presets", response_model=VariationPresetsResponse)
async def get_variation_presets():
    """Get available variation presets and their configurations."""
    presets_info = {}

    for preset_name, config in VARIATION_PRESETS.items():
        presets_info[preset_name] = {
            "angles": config.angles,
            "lighting": config.lighting,
            "backgrounds": config.backgrounds,
            "styles": config.styles,
            "estimated_count": len(config.angles) * len(config.lighting),
        }

    return VariationPresetsResponse(presets=presets_info)


@router.get("/jobs", response_model=List[JobStatusResponse])
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 20,
):
    """
    List batch generation jobs.

    Filter by status: pending, in_progress, completed, failed, cancelled
    """
    job_status = None
    if status:
        try:
            job_status = JobStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    jobs = batch_queue.list_jobs(
        job_type="batch_generation",
        status=job_status,
        limit=limit,
    )

    return [JobStatusResponse(**job.to_dict()) for job in jobs]
