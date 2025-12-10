"""Mockup generation endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.storage import get_image, save_image
from app.core.gemini import gemini_client
from app.core.scene_generator import get_template, build_customized_prompt
from app.core.utils import get_image_url
from app.models import Product, Mockup
from app.schemas import MockupGenerateRequest, MockupResponse

router = APIRouter()


@router.post("/generate", response_model=MockupResponse)
async def generate_mockup(
    request: MockupGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a mockup for a product.

    - Takes product ID and scene template
    - Supports customization (color, surface, lighting, angle)
    - Uses AI to generate the mockup
    - Saves and returns the result
    """
    # Get product
    result = await db.execute(select(Product).where(Product.id == request.product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get scene template
    template = get_template(request.scene_template_id or "studio-white")
    if not template:
        template = get_template("studio-white")

    # Build prompt with customizations
    if request.custom_prompt:
        scene_prompt = request.custom_prompt
    elif request.customization:
        customizations = {
            "color": request.customization.color,
            "surface": request.customization.surface,
            "lighting": request.customization.lighting,
            "angle": request.customization.angle,
        }
        scene_prompt = build_customized_prompt(template.id, customizations)
    else:
        scene_prompt = template.prompt

    # Load product image (use processed if available)
    image_path = product.processed_image_path or product.original_image_path
    product_image = get_image(image_path)

    # Generate mockup with AI
    mockup_image = await gemini_client.generate_mockup(
        product_image=product_image,
        scene_description=scene_prompt,
    )

    if not mockup_image:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate mockup. Please check your Gemini API key."
        )

    # Save mockup
    mockup_path = save_image(mockup_image, "mockups")

    # Build generation params for storage
    generation_params = {
        "scene_template": request.scene_template_id,
        "custom_prompt": request.custom_prompt,
    }
    if request.customization:
        generation_params["customization"] = request.customization.model_dump()

    # Create database record
    mockup = Mockup(
        product_id=product.id,
        image_path=mockup_path,
        scene_template_id=request.scene_template_id,
        prompt_used=scene_prompt,
        generation_params=generation_params,
    )
    db.add(mockup)
    await db.flush()
    await db.refresh(mockup)

    return MockupResponse(
        id=mockup.id,
        product_id=mockup.product_id,
        image_url=get_image_url(mockup.image_path),
        scene_template_id=mockup.scene_template_id,
        prompt_used=mockup.prompt_used,
        created_at=mockup.created_at,
    )


@router.get("/", response_model=list[MockupResponse])
async def list_mockups(
    db: AsyncSession = Depends(get_db),
    product_id: str = None,
    limit: int = 20,
):
    """List mockups, optionally filtered by product."""
    query = select(Mockup).order_by(Mockup.created_at.desc()).limit(limit)

    if product_id:
        query = query.where(Mockup.product_id == product_id)

    result = await db.execute(query)
    mockups = result.scalars().all()

    return [
        MockupResponse(
            id=m.id,
            product_id=m.product_id,
            image_url=get_image_url(m.image_path),
            scene_template_id=m.scene_template_id,
            prompt_used=m.prompt_used,
            created_at=m.created_at,
        )
        for m in mockups
    ]


@router.get("/{mockup_id}", response_model=MockupResponse)
async def get_mockup(
    mockup_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific mockup."""
    result = await db.execute(select(Mockup).where(Mockup.id == mockup_id))
    mockup = result.scalar_one_or_none()

    if not mockup:
        raise HTTPException(status_code=404, detail="Mockup not found")

    return MockupResponse(
        id=mockup.id,
        product_id=mockup.product_id,
        image_url=get_image_url(mockup.image_path),
        scene_template_id=mockup.scene_template_id,
        prompt_used=mockup.prompt_used,
        created_at=mockup.created_at,
    )


@router.delete("/{mockup_id}")
async def delete_mockup(
    mockup_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a mockup."""
    result = await db.execute(select(Mockup).where(Mockup.id == mockup_id))
    mockup = result.scalar_one_or_none()

    if not mockup:
        raise HTTPException(status_code=404, detail="Mockup not found")

    await db.delete(mockup)
    return {"message": "Mockup deleted", "id": mockup_id}
