"""Mockup generation endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.storage import get_image, save_image
from app.core.gemini import gemini_client
from app.core.compositor import compositor
from app.core.scene_generator import get_template, build_customized_prompt
from app.core.utils import get_image_url
from app.models import Product, Mockup, Brand
from app.schemas import MockupGenerateRequest, MockupResponse

router = APIRouter()


def _enhance_prompt_with_brand(base_prompt: str, brand: Brand) -> tuple[str, dict]:
    """Enhance a scene prompt with brand attributes."""
    attributes_applied = {}
    enhancements = []
    
    # Add color influence
    if brand.primary_color:
        enhancements.append(f"Color scheme influenced by {brand.primary_color}")
        attributes_applied["primary_color"] = brand.primary_color
    
    if brand.secondary_color:
        enhancements.append(f"accent elements in {brand.secondary_color}")
        attributes_applied["secondary_color"] = brand.secondary_color
    
    # Add mood influence
    if brand.mood:
        mood_descriptions = {
            "luxury": "luxurious, high-end feel with rich textures",
            "minimal": "clean, minimalist aesthetic with negative space",
            "playful": "vibrant, energetic atmosphere",
            "professional": "polished, business-appropriate setting",
            "elegant": "sophisticated, refined elegance",
            "bold": "striking, confident visual impact",
            "organic": "natural, earthy elements",
            "tech": "sleek, modern technology aesthetic",
        }
        mood_desc = mood_descriptions.get(brand.mood.lower(), f"{brand.mood} aesthetic")
        enhancements.append(mood_desc)
        attributes_applied["mood"] = brand.mood
    
    # Add lighting preference
    if brand.preferred_lighting:
        lighting_descriptions = {
            "dramatic": "dramatic lighting with strong shadows",
            "soft": "soft, diffused lighting",
            "bright": "bright, even illumination",
            "studio": "professional studio lighting",
            "natural": "natural daylight",
            "warm": "warm, golden hour lighting",
        }
        light_desc = lighting_descriptions.get(
            brand.preferred_lighting.lower(),
            f"{brand.preferred_lighting} lighting"
        )
        enhancements.append(light_desc)
        attributes_applied["lighting"] = brand.preferred_lighting
    
    # Build enhanced prompt
    if enhancements:
        enhanced = f"{base_prompt}. Brand styling: {', '.join(enhancements)}."
    else:
        enhanced = base_prompt
    
    return enhanced, attributes_applied


@router.post("/generate", response_model=MockupResponse)
async def generate_mockup(
    request: MockupGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a mockup for a product.

    - Takes product ID and scene template
    - Supports customization (color, surface, lighting, angle)
    - Supports brand DNA for consistent styling
    - Uses AI to generate the mockup
    - Saves and returns the result
    """
    # Get product
    result = await db.execute(select(Product).where(Product.id == request.product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get brand if specified
    brand: Optional[Brand] = None
    brand_applied = None
    
    if request.brand_id:
        result = await db.execute(select(Brand).where(Brand.id == request.brand_id))
        brand = result.scalar_one_or_none()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")

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
    
    # Apply brand styling to prompt
    if brand:
        scene_prompt, brand_applied = _enhance_prompt_with_brand(scene_prompt, brand)

    # Load product image (use processed if available)
    image_path = product.processed_image_path or product.original_image_path
    product_image = get_image(image_path)

    # Try generating a background and performing smart compositing first
    mockup_image = None
    pipeline_used = "smart_composite"

    background_image = await gemini_client.generate_scene_image(
        scene_prompt=scene_prompt,
        product_image=product_image,
    )

    if background_image:
        mockup_image = await compositor.smart_composite(
            product=product_image,
            background=background_image,
            lighting_hint=request.customization.lighting if request.customization else None,
            angle_hint=request.customization.angle if request.customization else None,
        )
    else:
        pipeline_used = "ai-direct"

    # Fallback to direct AI mockup if background generation/compositing fails
    if mockup_image is None:
        mockup_image = await gemini_client.generate_mockup(
            product_image=product_image,
            scene_description=scene_prompt,
        )
        pipeline_used = "ai-direct"

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
    if brand:
        generation_params["brand_id"] = brand.id
        generation_params["brand_name"] = brand.name
    generation_params["pipeline"] = pipeline_used

    # Create database record
    mockup = Mockup(
        product_id=product.id,
        brand_id=brand.id if brand else None,
        image_path=mockup_path,
        scene_template_id=request.scene_template_id,
        prompt_used=scene_prompt,
        generation_params=generation_params,
        brand_applied=brand_applied,
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
        brand_id=mockup.brand_id,
        brand_applied=mockup.brand_applied,
        created_at=mockup.created_at,
    )


@router.get("/", response_model=list[MockupResponse])
async def list_mockups(
    db: AsyncSession = Depends(get_db),
    product_id: str = None,
    brand_id: str = None,
    limit: int = 20,
):
    """List mockups, optionally filtered by product or brand."""
    query = select(Mockup).order_by(Mockup.created_at.desc()).limit(limit)

    if product_id:
        query = query.where(Mockup.product_id == product_id)
    if brand_id:
        query = query.where(Mockup.brand_id == brand_id)

    result = await db.execute(query)
    mockups = result.scalars().all()

    return [
        MockupResponse(
            id=m.id,
            product_id=m.product_id,
            image_url=get_image_url(m.image_path),
            scene_template_id=m.scene_template_id,
            prompt_used=m.prompt_used,
            brand_id=m.brand_id,
            brand_applied=m.brand_applied,
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
        brand_id=mockup.brand_id,
        brand_applied=mockup.brand_applied,
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
