"""Scene templates API endpoints."""
from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel

from app.core.scene_generator import (
    get_all_templates,
    get_templates_by_category,
    get_template,
    search_templates,
    get_categories,
    build_customized_prompt,
    SceneCategory,
    SceneTemplate,
)

router = APIRouter()


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


@router.get("/suggestions")
async def get_scene_suggestions(
    product_category: Optional[str] = Query(None, description="Product category for suggestions"),
):
    """
    Get AI-suggested scenes based on product category.

    Returns templates sorted by relevance for the product type.
    """
    # Category to scene mapping
    category_mapping = {
        "electronics": ["lifestyle-desk", "studio-white", "premium-dark", "ecommerce-amazon"],
        "beauty": ["lifestyle-bathroom", "premium-marble", "studio-gradient", "social-instagram"],
        "food": ["lifestyle-kitchen", "lifestyle-cafe", "outdoor-nature", "ecommerce-flat-lay"],
        "fashion": ["outdoor-urban", "studio-colored", "social-instagram", "premium-velvet"],
        "home": ["lifestyle-living-room", "lifestyle-bedroom", "studio-white", "social-pinterest"],
        "fitness": ["outdoor-nature", "studio-white", "outdoor-urban", "lifestyle-desk"],
        "jewelry": ["premium-velvet", "premium-marble", "premium-dark", "studio-white"],
        "tech": ["lifestyle-desk", "studio-gray", "premium-dark", "ecommerce-amazon"],
    }

    # Get suggested template IDs
    suggested_ids = category_mapping.get(
        product_category,
        ["studio-white", "lifestyle-desk", "ecommerce-amazon", "social-instagram"]
    )

    suggestions = []
    for i, template_id in enumerate(suggested_ids):
        template = get_template(template_id)
        if template:
            suggestions.append({
                "template": SceneTemplateResponse.from_template(template),
                "relevance": round(1.0 - (i * 0.15), 2),
                "reason": _get_suggestion_reason(template, product_category),
            })

    return {
        "product_category": product_category,
        "suggestions": suggestions,
    }


def _get_suggestion_reason(template: SceneTemplate, product_category: Optional[str]) -> str:
    """Generate a reason for the suggestion."""
    reasons = {
        "studio-white": "Clean background ideal for product listings",
        "studio-gray": "Neutral backdrop that complements any product",
        "lifestyle-desk": "Shows product in a relatable workspace context",
        "lifestyle-kitchen": "Perfect context for food and kitchen items",
        "lifestyle-bathroom": "Ideal setting for beauty and self-care products",
        "lifestyle-bedroom": "Cozy atmosphere for home and wellness products",
        "lifestyle-cafe": "Trendy setting for food and lifestyle brands",
        "outdoor-nature": "Natural setting for eco-conscious products",
        "outdoor-urban": "Edgy backdrop for fashion and streetwear",
        "premium-dark": "Dramatic lighting for luxury appeal",
        "premium-marble": "Elegant surface for premium positioning",
        "premium-velvet": "Luxurious texture for jewelry and accessories",
        "ecommerce-amazon": "Meets marketplace image requirements",
        "ecommerce-flat-lay": "Perfect for social media and catalogs",
        "social-instagram": "Optimized for social media engagement",
        "social-pinterest": "Designed for high save rates",
    }
    return reasons.get(template.id, f"Great match for {product_category or 'your'} products")
