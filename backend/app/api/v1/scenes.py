"""Scene templates endpoints."""
from fastapi import APIRouter
from typing import Optional

from app.core.scene_generator import SCENE_TEMPLATES

router = APIRouter()


@router.get("/templates")
async def list_scene_templates(category: Optional[str] = None):
    """List available scene templates."""
    templates = []

    for template_id, template in SCENE_TEMPLATES.items():
        if category and template["category"] != category:
            continue

        templates.append({
            "id": template_id,
            "name": template["name"],
            "category": template["category"],
            "tags": template.get("tags", []),
        })

    return {"templates": templates}


@router.get("/templates/{template_id}")
async def get_scene_template(template_id: str):
    """Get a specific scene template."""
    template = SCENE_TEMPLATES.get(template_id)

    if not template:
        return {"error": "Template not found"}

    return {
        "id": template_id,
        **template,
    }


@router.get("/categories")
async def list_categories():
    """List all scene categories."""
    categories = set()
    for template in SCENE_TEMPLATES.values():
        categories.add(template["category"])

    return {"categories": sorted(list(categories))}
