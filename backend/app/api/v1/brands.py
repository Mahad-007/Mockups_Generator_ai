"""Brand management API endpoints."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
import logging

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.storage import save_image, get_image
from app.core.utils import get_image_url
from app.models import Brand, User
from app.schemas import (
    BrandCreate,
    BrandUpdate,
    BrandResponse,
    BrandExtractRequest,
    BrandExtractResponse,
    BrandPromptResponse,
    BrandScenesResponse,
)
from app.services.usage_service import ensure_within_limits

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=BrandResponse)
async def create_brand(
    brand: BrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new brand profile.
    
    Brand profiles store colors, typography, mood, and style preferences
    that influence mockup generation for consistent branding.
    """
    # If setting as default, unset any existing defaults
    if brand.is_default:
        await db.execute(
            update(Brand).where(Brand.is_default == True).values(is_default=False)
        )
    
    # Generate prompt description from brand attributes
    prompt_description = _generate_prompt_description(brand)
    
    # Determine suggested scenes based on mood/style
    suggested_scenes = _get_suggested_scenes(brand.mood, brand.style, brand.industry)
    
    # Determine preferred lighting based on mood
    preferred_lighting = brand.preferred_lighting or _get_preferred_lighting(brand.mood)
    
    await ensure_within_limits(db, current_user, "brands_created", increment=1)

    db_brand = Brand(
        user_id=current_user.id,
        name=brand.name,
        description=brand.description,
        website_url=brand.website_url,
        primary_color=brand.primary_color,
        secondary_color=brand.secondary_color,
        accent_color=brand.accent_color,
        background_color=brand.background_color,
        color_palette=brand.color_palette,
        primary_font=brand.primary_font,
        secondary_font=brand.secondary_font,
        font_style=brand.font_style,
        mood=brand.mood,
        style=brand.style,
        industry=brand.industry,
        target_audience=brand.target_audience,
        prompt_description=prompt_description,
        suggested_scenes=suggested_scenes,
        preferred_lighting=preferred_lighting,
        is_default=brand.is_default,
        is_extracted=False,
    )
    
    db.add(db_brand)
    await db.flush()
    await db.refresh(db_brand)
    
    return BrandResponse.model_validate(db_brand)


@router.get("/", response_model=List[BrandResponse])
async def list_brands(
    db: AsyncSession = Depends(get_db),
    include_default: bool = True,
    current_user: User = Depends(get_current_active_user),
):
    """List all brands for the current user."""
    query = (
        select(Brand)
        .where(Brand.user_id == current_user.id)
        .order_by(Brand.is_default.desc(), Brand.created_at.desc())
    )
    
    result = await db.execute(query)
    brands = result.scalars().all()
    
    return [BrandResponse.model_validate(b) for b in brands]


@router.get("/default", response_model=Optional[BrandResponse])
async def get_default_brand(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get the default brand profile."""
    result = await db.execute(
        select(Brand).where(Brand.is_default == True, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        return None
    
    return BrandResponse.model_validate(brand)


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific brand by ID."""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    return BrandResponse.model_validate(brand)


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: str,
    brand_update: BrandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a brand profile."""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # If setting as default, unset any existing defaults
    if brand_update.is_default:
        await db.execute(
            update(Brand)
            .where(Brand.is_default == True, Brand.id != brand_id)
            .values(is_default=False)
        )
    
    # Update fields
    update_data = brand_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(brand, key, value)
    
    # Regenerate prompt description if relevant fields changed
    if any(k in update_data for k in ['mood', 'style', 'primary_color', 'secondary_color', 'industry']):
        brand.prompt_description = _generate_prompt_description_from_brand(brand)
        brand.suggested_scenes = _get_suggested_scenes(brand.mood, brand.style, brand.industry)
        brand.preferred_lighting = brand.preferred_lighting or _get_preferred_lighting(brand.mood)
    
    await db.flush()
    await db.refresh(brand)
    
    return BrandResponse.model_validate(brand)


@router.delete("/{brand_id}")
async def delete_brand(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a brand."""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    await db.delete(brand)
    
    return {"message": "Brand deleted", "id": brand_id}


@router.post("/{brand_id}/set-default", response_model=BrandResponse)
async def set_default_brand(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Set a brand as the default."""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Unset all other defaults
    await db.execute(
        update(Brand).where(Brand.id != brand_id).values(is_default=False)
    )
    
    # Set this brand as default
    brand.is_default = True
    await db.flush()
    await db.refresh(brand)
    
    return BrandResponse.model_validate(brand)


@router.post("/{brand_id}/upload-logo", response_model=BrandResponse)
async def upload_brand_logo(
    brand_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a logo for a brand."""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Save logo image
    from PIL import Image
    import io
    
    contents = await file.read()
    logo_image = Image.open(io.BytesIO(contents))
    
    # Save to logos directory
    logo_path = save_image(logo_image, "logos")
    brand.logo_url = get_image_url(logo_path)
    
    await db.flush()
    await db.refresh(brand)
    
    return BrandResponse.model_validate(brand)


@router.post("/extract", response_model=BrandExtractResponse)
async def extract_brand(
    logo: Optional[UploadFile] = File(None),
    website_url: Optional[str] = Form(None),
    brand_name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Extract brand colors and style from logo or website.
    
    Uses AI to analyze:
    - Logo image: Extracts color palette and visual style
    - Website URL: Analyzes design, colors, typography hints
    - Combines both for comprehensive brand DNA
    """
    from app.core.brand_extractor import brand_extractor
    
    extracted_data = {
        "primary_color": None,
        "secondary_color": None,
        "accent_color": None,
        "color_palette": [],
        "mood": None,
        "style": None,
        "industry": None,
    }
    confidence = 0.5
    suggestions = []
    
    # Extract from logo if provided
    if logo:
        try:
            from PIL import Image
            import io
            
            contents = await logo.read()
            logo_image = Image.open(io.BytesIO(contents))
            
            logo_result = await brand_extractor.extract_from_logo(logo_image)
            extracted_data.update(logo_result.get("colors", {}))
            extracted_data["mood"] = logo_result.get("mood")
            extracted_data["style"] = logo_result.get("style")
            confidence = max(confidence, logo_result.get("confidence", 0.6))
            
        except Exception as e:
            logger.error(f"Logo extraction failed: {e}")
            suggestions.append("Logo analysis failed - try a clearer image")
    
    # Extract from website if provided
    if website_url:
        try:
            web_result = await brand_extractor.extract_from_website(website_url)
            
            # Merge with logo results, preferring logo colors
            if not extracted_data["primary_color"]:
                extracted_data["primary_color"] = web_result.get("primary_color")
            if not extracted_data["secondary_color"]:
                extracted_data["secondary_color"] = web_result.get("secondary_color")
            if not extracted_data["mood"]:
                extracted_data["mood"] = web_result.get("mood")
            if not extracted_data["style"]:
                extracted_data["style"] = web_result.get("style")
            if not extracted_data["industry"]:
                extracted_data["industry"] = web_result.get("industry")
                
            # Extend color palette
            web_colors = web_result.get("color_palette", [])
            extracted_data["color_palette"] = list(set(
                extracted_data.get("color_palette", []) + web_colors
            ))[:8]  # Limit to 8 colors
            
            confidence = max(confidence, web_result.get("confidence", 0.7))
            
        except Exception as e:
            logger.error(f"Website extraction failed: {e}")
            suggestions.append("Website analysis failed - check URL accessibility")
    
    # AI analysis using Gemini if we have data
    if logo or website_url:
        try:
            ai_result = await brand_extractor.analyze_brand_mood(
                extracted_data,
                brand_name=brand_name,
            )
            if ai_result.get("mood"):
                extracted_data["mood"] = ai_result["mood"]
            if ai_result.get("style"):
                extracted_data["style"] = ai_result["style"]
            if ai_result.get("industry"):
                extracted_data["industry"] = ai_result["industry"]
            if ai_result.get("target_audience"):
                extracted_data["target_audience"] = ai_result["target_audience"]
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
    
    # Generate suggestions
    if not extracted_data["primary_color"]:
        suggestions.append("Upload a logo or provide a website for better color extraction")
    if not extracted_data["mood"]:
        suggestions.append("Set a mood manually for better mockup generation")
    
    return BrandExtractResponse(
        extracted=extracted_data,
        confidence=confidence,
        suggestions=suggestions,
    )


@router.post("/extract-and-create", response_model=BrandResponse)
async def extract_and_create_brand(
    name: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    website_url: Optional[str] = Form(None),
    is_default: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Extract brand from logo/website and create a new brand profile.
    
    Combines extraction and creation in one step for convenience.
    """
    from app.core.brand_extractor import brand_extractor
    
    extracted = {}
    logo_path = None
    
    # Extract from logo
    if logo:
        try:
            from PIL import Image
            import io
            
            contents = await logo.read()
            logo_image = Image.open(io.BytesIO(contents))
            
            # Save logo
            logo_path = save_image(logo_image, "logos")
            
            # Extract colors and style
            logo_result = await brand_extractor.extract_from_logo(logo_image)
            extracted.update(logo_result.get("colors", {}))
            extracted["mood"] = logo_result.get("mood")
            extracted["style"] = logo_result.get("style")
            
        except Exception as e:
            logger.error(f"Logo extraction failed: {e}")
    
    # Extract from website
    if website_url:
        try:
            web_result = await brand_extractor.extract_from_website(website_url)
            for key in ["primary_color", "secondary_color", "accent_color", "mood", "style", "industry"]:
                if not extracted.get(key):
                    extracted[key] = web_result.get(key)
                    
        except Exception as e:
            logger.error(f"Website extraction failed: {e}")
    
    # AI mood analysis
    if extracted:
        try:
            ai_result = await brand_extractor.analyze_brand_mood(extracted, brand_name=name)
            for key in ["mood", "style", "industry", "target_audience"]:
                if ai_result.get(key):
                    extracted[key] = ai_result[key]
        except Exception:
            pass
    
    # Enforce usage limits
    await ensure_within_limits(db, current_user, "brands_created", increment=1)

    # If setting as default, unset others
    if is_default:
        await db.execute(
            update(Brand).where(Brand.is_default == True).values(is_default=False)
        )
    
    # Generate prompt description
    prompt_description = _generate_prompt_description_dict(extracted)
    suggested_scenes = _get_suggested_scenes(
        extracted.get("mood"), 
        extracted.get("style"), 
        extracted.get("industry")
    )
    preferred_lighting = _get_preferred_lighting(extracted.get("mood"))
    
    # Create brand
    db_brand = Brand(
        user_id=current_user.id,
        name=name,
        website_url=website_url,
        logo_url=get_image_url(logo_path) if logo_path else None,
        primary_color=extracted.get("primary_color"),
        secondary_color=extracted.get("secondary_color"),
        accent_color=extracted.get("accent_color"),
        color_palette=extracted.get("color_palette"),
        mood=extracted.get("mood"),
        style=extracted.get("style"),
        industry=extracted.get("industry"),
        target_audience=extracted.get("target_audience"),
        prompt_description=prompt_description,
        suggested_scenes=suggested_scenes,
        preferred_lighting=preferred_lighting,
        is_default=is_default,
        is_extracted=True,
    )
    
    db.add(db_brand)
    await db.flush()
    await db.refresh(db_brand)
    
    return BrandResponse.model_validate(db_brand)


@router.get("/{brand_id}/prompt", response_model=BrandPromptResponse)
async def get_brand_prompt(
    brand_id: str,
    base_prompt: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a brand-enhanced version of a scene prompt.
    
    Takes a base scene prompt and enhances it with brand attributes
    for consistent brand styling in mockups.
    """
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    enhanced_prompt, attributes = _enhance_prompt_with_brand(base_prompt, brand)
    
    return BrandPromptResponse(
        brand_id=brand_id,
        original_prompt=base_prompt,
        brand_enhanced_prompt=enhanced_prompt,
        brand_attributes_applied=attributes,
    )


@router.get("/{brand_id}/suggested-scenes", response_model=BrandScenesResponse)
async def get_brand_scenes(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get scene template suggestions based on brand attributes.
    
    Returns scenes that match the brand's mood, style, and industry.
    """
    from app.core.scene_generator import get_template
    
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Get suggested scene IDs
    scene_ids = brand.suggested_scenes or _get_suggested_scenes(
        brand.mood, brand.style, brand.industry
    )
    
    suggestions = []
    for i, scene_id in enumerate(scene_ids):
        template = get_template(scene_id)
        if template:
            suggestions.append({
                "template_id": scene_id,
                "name": template.name,
                "description": template.description,
                "reason": _get_scene_reason(scene_id, brand),
                "relevance": round(1.0 - (i * 0.1), 2),
            })
    
    return BrandScenesResponse(
        brand_id=brand_id,
        brand_mood=brand.mood,
        brand_style=brand.style,
        suggested_scenes=suggestions,
    )


# Helper functions

def _generate_prompt_description(brand: BrandCreate) -> str:
    """Generate an AI prompt description from brand attributes."""
    parts = []
    
    if brand.mood:
        parts.append(f"{brand.mood} aesthetic")
    if brand.style:
        parts.append(f"{brand.style} style")
    if brand.primary_color:
        parts.append(f"featuring {brand.primary_color} as primary color")
    if brand.secondary_color:
        parts.append(f"with {brand.secondary_color} accents")
    if brand.industry:
        parts.append(f"suitable for {brand.industry} industry")
    if brand.target_audience:
        parts.append(f"targeting {brand.target_audience}")
    
    if not parts:
        return "Clean, professional product photography"
    
    return "Product mockup with " + ", ".join(parts)


def _generate_prompt_description_from_brand(brand: Brand) -> str:
    """Generate prompt description from existing brand model."""
    parts = []
    
    if brand.mood:
        parts.append(f"{brand.mood} aesthetic")
    if brand.style:
        parts.append(f"{brand.style} style")
    if brand.primary_color:
        parts.append(f"featuring {brand.primary_color} as primary color")
    if brand.secondary_color:
        parts.append(f"with {brand.secondary_color} accents")
    if brand.industry:
        parts.append(f"suitable for {brand.industry} industry")
    
    if not parts:
        return "Clean, professional product photography"
    
    return "Product mockup with " + ", ".join(parts)


def _generate_prompt_description_dict(data: dict) -> str:
    """Generate prompt description from dictionary."""
    parts = []
    
    if data.get("mood"):
        parts.append(f"{data['mood']} aesthetic")
    if data.get("style"):
        parts.append(f"{data['style']} style")
    if data.get("primary_color"):
        parts.append(f"featuring {data['primary_color']} as primary color")
    if data.get("industry"):
        parts.append(f"suitable for {data['industry']} industry")
    
    if not parts:
        return "Clean, professional product photography"
    
    return "Product mockup with " + ", ".join(parts)


def _get_suggested_scenes(mood: Optional[str], style: Optional[str], industry: Optional[str]) -> List[str]:
    """Get suggested scene templates based on brand attributes."""
    scenes = []
    
    # Industry-based suggestions
    industry_scenes = {
        "tech": ["lifestyle-desk", "studio-white", "premium-dark"],
        "beauty": ["lifestyle-bathroom", "premium-marble", "social-instagram"],
        "food": ["lifestyle-kitchen", "lifestyle-cafe", "outdoor-nature"],
        "fashion": ["outdoor-urban", "studio-colored", "social-instagram"],
        "home": ["lifestyle-living-room", "lifestyle-bedroom", "studio-white"],
        "fitness": ["outdoor-nature", "studio-white", "outdoor-urban"],
        "jewelry": ["premium-velvet", "premium-marble", "premium-dark"],
        "electronics": ["lifestyle-desk", "studio-gray", "premium-dark"],
    }
    
    if industry and industry.lower() in industry_scenes:
        scenes.extend(industry_scenes[industry.lower()])
    
    # Mood-based additions
    mood_scenes = {
        "luxury": ["premium-dark", "premium-marble", "premium-velvet"],
        "minimal": ["studio-white", "studio-gray", "lifestyle-desk"],
        "playful": ["studio-colored", "social-instagram", "outdoor-nature"],
        "professional": ["studio-white", "lifestyle-desk", "ecommerce-amazon"],
        "elegant": ["premium-marble", "premium-velvet", "studio-gradient"],
        "bold": ["studio-colored", "premium-dark", "outdoor-urban"],
    }
    
    if mood and mood.lower() in mood_scenes:
        for scene in mood_scenes[mood.lower()]:
            if scene not in scenes:
                scenes.append(scene)
    
    # Default scenes if none matched
    if not scenes:
        scenes = ["studio-white", "lifestyle-desk", "ecommerce-amazon", "social-instagram"]
    
    return scenes[:6]  # Return top 6


def _get_preferred_lighting(mood: Optional[str]) -> str:
    """Get preferred lighting based on brand mood."""
    lighting_map = {
        "luxury": "dramatic",
        "minimal": "soft",
        "playful": "bright",
        "professional": "studio",
        "elegant": "soft",
        "bold": "dramatic",
        "casual": "natural",
        "organic": "natural",
        "tech": "studio",
        "vintage": "warm",
    }
    
    if mood and mood.lower() in lighting_map:
        return lighting_map[mood.lower()]
    
    return "natural"


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


def _get_scene_reason(scene_id: str, brand: Brand) -> str:
    """Generate a reason why this scene matches the brand."""
    reasons = {
        "studio-white": "Clean backdrop complements your brand's clarity",
        "studio-gray": "Neutral setting lets your brand colors stand out",
        "studio-colored": "Vibrant background matches your brand energy",
        "lifestyle-desk": "Professional workspace aligns with your audience",
        "lifestyle-kitchen": "Lifestyle context resonates with your industry",
        "lifestyle-bathroom": "Self-care setting suits your beauty brand",
        "premium-dark": "Dramatic backdrop elevates your luxury positioning",
        "premium-marble": "Elegant surface matches your sophisticated style",
        "premium-velvet": "Rich texture complements your premium brand",
        "outdoor-nature": "Natural setting aligns with your organic values",
        "outdoor-urban": "Urban edge matches your bold aesthetic",
        "social-instagram": "Optimized for your social media presence",
        "ecommerce-amazon": "Marketplace-ready for your sales channels",
    }
    
    base_reason = reasons.get(scene_id, "Great match for your brand")
    
    if brand.mood:
        base_reason = f"{base_reason} ({brand.mood} mood)"
    
    return base_reason
