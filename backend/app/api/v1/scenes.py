"""Scene templates API endpoints."""
import logging
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.scene_generator import (
    get_all_templates,
    get_templates_by_category,
    get_template,
    search_templates,
    get_categories,
    build_customized_prompt,
    SceneCategory,
    SceneTemplate,
    build_scene_suggestions,
)
from app.core.database import get_db
from app.models import Product, Brand

router = APIRouter()
logger = logging.getLogger(__name__)


# Response schemas
class CustomizationOptionsResponse(BaseModel):
    colors: List[str]
    surfaces: List[str]
    lighting: List[str]
    angles: List[str]


class SceneTemplateResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    tags: List[str]
    is_premium: bool
    popularity: int
    customization: CustomizationOptionsResponse

    @classmethod
    def from_template(cls, template: SceneTemplate) -> "SceneTemplateResponse":
        return cls(
            id=template.id,
            name=template.name,
            category=template.category.value,
            description=template.description,
            tags=template.tags,
            is_premium=template.is_premium,
            popularity=template.popularity,
            customization=CustomizationOptionsResponse(
                colors=template.customization.colors,
                surfaces=template.customization.surfaces,
                lighting=template.customization.lighting,
                angles=template.customization.angles,
            ),
        )


class CustomizeRequest(BaseModel):
    template_id: str
    color: Optional[str] = None
    surface: Optional[str] = None
    lighting: Optional[str] = None
    angle: Optional[str] = None


class SceneSuggestionReason(BaseModel):
    label: str
    detail: str


class SceneSuggestionItem(BaseModel):
    template: SceneTemplateResponse
    relevance: float
    reasons: List[SceneSuggestionReason]
    trending: bool = False
    seasonal: Optional[str] = None
    feedback_token: str


class SceneSuggestionsResponse(BaseModel):
    product_category: Optional[str]
    product_attributes: dict
    brand_context: dict
    suggestions: List[SceneSuggestionItem]
    seasonal_context: Optional[str] = None


class SuggestionFeedbackRequest(BaseModel):
    feedback_token: str
    scene_id: str
    helpful: bool
    product_id: Optional[str] = None
    brand_id: Optional[str] = None
    notes: Optional[str] = None


@router.get("/templates", response_model=dict)
async def list_scene_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search templates"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    premium_only: bool = Query(False, description="Show only premium templates"),
    limit: int = Query(50, ge=1, le=100),
):
    """
    List available scene templates with filtering options.

    - Filter by category (studio, lifestyle, outdoor, etc.)
    - Search by name, description, or tags
    - Filter by tags
    - Filter premium templates
    """
    # Get templates based on filters
    if search:
        templates = search_templates(search)
    elif category:
        try:
            cat_enum = SceneCategory(category)
            templates = get_templates_by_category(cat_enum)
        except ValueError:
            templates = get_all_templates()
    else:
        templates = get_all_templates()

    # Apply tag filter
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",")]
        templates = [
            t for t in templates
            if any(tag in t.tags for tag in tag_list)
        ]

    # Apply premium filter
    if premium_only:
        templates = [t for t in templates if t.is_premium]

    # Apply limit
    templates = templates[:limit]

    return {
        "templates": [SceneTemplateResponse.from_template(t) for t in templates],
        "total": len(templates),
    }


@router.get("/templates/{template_id}", response_model=SceneTemplateResponse)
async def get_scene_template(template_id: str):
    """Get details for a specific scene template including customization options."""
    template = get_template(template_id)

    if not template:
        return {"error": "Template not found"}

    return SceneTemplateResponse.from_template(template)


@router.get("/categories")
async def list_categories():
    """List all scene categories with counts."""
    categories = get_categories()
    all_templates = get_all_templates()

    category_counts = {}
    for cat in categories:
        count = len([t for t in all_templates if t.category.value == cat])
        category_counts[cat] = count

    return {
        "categories": categories,
        "counts": category_counts,
    }


@router.get("/tags")
async def list_tags():
    """List all unique tags across templates."""
    all_templates = get_all_templates()
    tags = set()
    for template in all_templates:
        tags.update(template.tags)

    # Sort by frequency
    tag_counts = {}
    for tag in tags:
        count = sum(1 for t in all_templates if tag in t.tags)
        tag_counts[tag] = count

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        "tags": [{"name": t[0], "count": t[1]} for t in sorted_tags],
    }


@router.post("/customize")
async def customize_template(request: CustomizeRequest):
    """
    Get a customized prompt based on template and options.

    Useful for previewing what the final prompt will look like.
    """
    template = get_template(request.template_id)

    if not template:
        return {"error": "Template not found"}

    customizations = {
        "color": request.color,
        "surface": request.surface,
        "lighting": request.lighting,
        "angle": request.angle,
    }

    customized_prompt = build_customized_prompt(request.template_id, customizations)

    return {
        "template_id": request.template_id,
        "original_prompt": template.prompt,
        "customized_prompt": customized_prompt,
        "customizations_applied": {k: v for k, v in customizations.items() if v},
    }


@router.get("/suggestions", response_model=SceneSuggestionsResponse)
async def get_scene_suggestions(
    product_id: Optional[str] = Query(None, description="Product ID to base suggestions on"),
    product_category: Optional[str] = Query(None, description="Override category for suggestions"),
    brand_id: Optional[str] = Query(None, description="Optional brand to align with"),
    limit: int = Query(6, ge=3, le=12),
    db: AsyncSession = Depends(get_db),
):
    """
    Context-aware scene suggestions using product analysis + brand mood.

    - Reads product attributes (category, primary_color, style)
    - Blends brand mood/style/industry if provided
    - Adds trending and seasonal signals
    """
    attributes = {}
    brand_context = {}

    # Load product context when provided
    if product_id:
        product_result = await db.execute(select(Product).where(Product.id == product_id))
        product = product_result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.attributes:
            attributes = product.attributes
        if product.category and not product_category:
            product_category = product.category

    # Load brand context
    if brand_id:
        brand_result = await db.execute(select(Brand).where(Brand.id == brand_id))
        brand = brand_result.scalar_one_or_none()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")

        brand_context = {
            "mood": brand.mood,
            "style": brand.style,
            "industry": brand.industry,
            "preferred_lighting": brand.preferred_lighting,
            "suggested_scenes": brand.suggested_scenes or [],
        }

    raw_suggestions = build_scene_suggestions(
        product_category=product_category,
        attributes=attributes,
        brand_context=brand_context,
        limit=limit,
    )

    suggestions = [
        SceneSuggestionItem(
            template=SceneTemplateResponse.from_template(item["template"]),
            relevance=item["relevance"],
            reasons=[SceneSuggestionReason(**reason) for reason in item.get("reasons", [])],
            trending=item.get("trending", False),
            seasonal=item.get("seasonal"),
            feedback_token=item.get("feedback_token", f"{item['template'].id}:{product_category or 'general'}"),
        )
        for item in raw_suggestions
    ]

    # Seasonal context derived from any seasonal match
    seasonal_context = next((item.get("seasonal") for item in raw_suggestions if item.get("seasonal")), None)

    return SceneSuggestionsResponse(
        product_category=product_category,
        product_attributes=attributes,
        brand_context=brand_context,
        suggestions=suggestions,
        seasonal_context=seasonal_context,
    )


@router.post("/suggestions/feedback")
async def submit_suggestion_feedback(feedback: SuggestionFeedbackRequest):
    """
    Capture quick feedback to refine suggestions over time.

    Currently persisted in logs; can be wired to analytics later.
    """
    logger.info(
        "Scene suggestion feedback",
        extra={
            "token": feedback.feedback_token,
            "scene_id": feedback.scene_id,
            "helpful": feedback.helpful,
            "product_id": feedback.product_id,
            "brand_id": feedback.brand_id,
            "notes": feedback.notes,
        },
    )
    return {"message": "Feedback captured", "scene_id": feedback.scene_id, "helpful": feedback.helpful}
