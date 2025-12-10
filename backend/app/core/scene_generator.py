from typing import Optional, List, Dict
from app.core.gemini import gemini_client


# Scene template definitions
SCENE_TEMPLATES = {
    # Studio scenes
    "studio-white": {
        "name": "White Studio",
        "category": "studio",
        "prompt": "Clean white photography studio background, soft diffused lighting, professional product photography setup, minimalist, high-key lighting",
        "tags": ["minimal", "e-commerce", "clean"],
    },
    "studio-gradient": {
        "name": "Gradient Studio",
        "category": "studio",
        "prompt": "Elegant gradient background transitioning from light to dark, professional studio lighting, smooth seamless backdrop",
        "tags": ["modern", "professional", "versatile"],
    },
    "studio-colored": {
        "name": "Colored Backdrop",
        "category": "studio",
        "prompt": "Solid colored photography backdrop, soft studio lighting, professional product photography setup",
        "tags": ["bold", "colorful", "branding"],
    },

    # Lifestyle scenes
    "lifestyle-desk": {
        "name": "Modern Desk Setup",
        "category": "lifestyle",
        "prompt": "Modern minimalist desk setup, wooden desk surface, plants, natural window light, cozy workspace aesthetic, lifestyle product photography",
        "tags": ["tech", "workspace", "modern"],
    },
    "lifestyle-kitchen": {
        "name": "Kitchen Counter",
        "category": "lifestyle",
        "prompt": "Clean modern kitchen counter, marble or granite surface, natural light from window, plants and kitchen accessories, lifestyle photography",
        "tags": ["food", "home", "kitchen"],
    },
    "lifestyle-bathroom": {
        "name": "Bathroom Shelf",
        "category": "lifestyle",
        "prompt": "Elegant bathroom shelf or vanity, white marble surface, soft lighting, spa-like atmosphere, beauty product photography",
        "tags": ["beauty", "skincare", "spa"],
    },
    "lifestyle-bedroom": {
        "name": "Cozy Bedroom",
        "category": "lifestyle",
        "prompt": "Cozy bedroom setting, soft bedding, warm natural light, minimalist decor, lifestyle product photography",
        "tags": ["home", "comfort", "lifestyle"],
    },

    # Outdoor scenes
    "outdoor-nature": {
        "name": "Natural Outdoor",
        "category": "outdoor",
        "prompt": "Natural outdoor setting, soft grass or moss surface, dappled sunlight through trees, organic aesthetic, nature product photography",
        "tags": ["nature", "organic", "eco"],
    },
    "outdoor-urban": {
        "name": "Urban Street",
        "category": "outdoor",
        "prompt": "Urban street scene, concrete or brick surface, city atmosphere, modern streetwear aesthetic, urban product photography",
        "tags": ["street", "urban", "fashion"],
    },
    "outdoor-beach": {
        "name": "Beach Setting",
        "category": "outdoor",
        "prompt": "Beautiful beach setting, soft sand surface, ocean in background, golden hour lighting, summer vacation aesthetic",
        "tags": ["summer", "beach", "vacation"],
    },

    # E-commerce optimized
    "ecommerce-amazon": {
        "name": "Amazon Standard",
        "category": "e-commerce",
        "prompt": "Pure white background, professional product photography, bright even lighting, clean isolated product shot, e-commerce standard",
        "tags": ["amazon", "e-commerce", "white"],
    },
    "ecommerce-lifestyle": {
        "name": "E-commerce Lifestyle",
        "category": "e-commerce",
        "prompt": "Lifestyle product photography, clean modern setting, professional lighting, context showing product in use",
        "tags": ["lifestyle", "e-commerce", "context"],
    },

    # Premium/Luxury
    "premium-dark": {
        "name": "Dark Luxury",
        "category": "premium",
        "prompt": "Dark luxury backdrop, dramatic lighting, premium product photography, elegant shadows, high-end aesthetic",
        "tags": ["luxury", "premium", "dark"],
    },
    "premium-marble": {
        "name": "Marble Surface",
        "category": "premium",
        "prompt": "Elegant white marble surface, luxury product photography, soft diffused lighting, premium aesthetic, gold accents",
        "tags": ["luxury", "elegant", "marble"],
    },

    # Seasonal
    "seasonal-summer": {
        "name": "Summer Vibes",
        "category": "seasonal",
        "prompt": "Bright summer setting, tropical plants, vibrant colors, sunny atmosphere, summer product photography",
        "tags": ["summer", "tropical", "bright"],
    },
    "seasonal-winter": {
        "name": "Winter Cozy",
        "category": "seasonal",
        "prompt": "Cozy winter setting, soft white snow or fur, warm lighting, hygge aesthetic, winter product photography",
        "tags": ["winter", "cozy", "holiday"],
    },
    "seasonal-autumn": {
        "name": "Autumn Warmth",
        "category": "seasonal",
        "prompt": "Warm autumn setting, fallen leaves, wooden surface, golden hour lighting, cozy fall aesthetic",
        "tags": ["autumn", "fall", "warm"],
    },
    "seasonal-spring": {
        "name": "Spring Fresh",
        "category": "seasonal",
        "prompt": "Fresh spring setting, flowers and greenery, bright natural light, renewal aesthetic, spring product photography",
        "tags": ["spring", "fresh", "flowers"],
    },
}


class SceneGenerator:
    """Generates scene backgrounds for product mockups."""

    def __init__(self):
        self.templates = SCENE_TEMPLATES

    def get_templates(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Get available scene templates with optional filtering."""
        templates = []

        for template_id, template in self.templates.items():
            if category and template["category"] != category:
                continue

            if tags:
                if not any(tag in template["tags"] for tag in tags):
                    continue

            templates.append({
                "id": template_id,
                **template,
            })

        return templates

    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get a specific template by ID."""
        if template_id not in self.templates:
            return None
        return {"id": template_id, **self.templates[template_id]}

    async def generate_scene(
        self,
        template_id: str,
        customizations: Optional[Dict] = None,
        brand_colors: Optional[List[str]] = None,
    ) -> bytes:
        """
        Generate a scene image from a template.

        Args:
            template_id: ID of the scene template
            customizations: Optional customizations (color, lighting, etc.)
            brand_colors: Optional brand colors to incorporate

        Returns:
            Image bytes of the generated scene
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        prompt = template["prompt"]

        # Apply customizations
        if customizations:
            if "color" in customizations:
                prompt += f", {customizations['color']} color scheme"
            if "lighting" in customizations:
                prompt += f", {customizations['lighting']} lighting"
            if "surface" in customizations:
                prompt += f", {customizations['surface']} surface"
            if "mood" in customizations:
                prompt += f", {customizations['mood']} mood"

        # Generate scene using Gemini
        return await gemini_client.generate_scene(
            scene_prompt=prompt,
            brand_colors=brand_colors,
            style=template.get("category", "professional"),
        )

    async def suggest_scenes(
        self,
        product_category: str,
        product_attributes: Dict,
        brand_mood: Optional[str] = None,
    ) -> List[Dict]:
        """
        Suggest appropriate scene templates for a product.

        Args:
            product_category: Category of the product
            product_attributes: Product attributes (color, style, etc.)
            brand_mood: Brand mood if available

        Returns:
            List of suggested templates with relevance scores
        """
        # Category to scene mapping
        category_scenes = {
            "electronics": ["lifestyle-desk", "studio-white", "premium-dark"],
            "beauty": ["lifestyle-bathroom", "premium-marble", "studio-gradient"],
            "food": ["lifestyle-kitchen", "outdoor-nature", "seasonal-summer"],
            "fashion": ["outdoor-urban", "studio-colored", "lifestyle-bedroom"],
            "home": ["lifestyle-bedroom", "lifestyle-kitchen", "studio-white"],
            "fitness": ["outdoor-nature", "studio-white", "outdoor-urban"],
        }

        # Get base suggestions from category
        suggested_ids = category_scenes.get(product_category, ["studio-white", "lifestyle-desk"])

        # Add e-commerce templates
        suggested_ids.extend(["ecommerce-amazon", "ecommerce-lifestyle"])

        # Add seasonal if relevant
        # (Could be enhanced with date-based logic)

        suggestions = []
        for i, template_id in enumerate(suggested_ids[:6]):  # Top 6
            template = self.get_template(template_id)
            if template:
                relevance = 1.0 - (i * 0.1)  # Decreasing relevance
                suggestions.append({
                    **template,
                    "relevance": round(relevance, 2),
                    "reason": self._get_suggestion_reason(template, product_category),
                })

        return suggestions

    def _get_suggestion_reason(self, template: Dict, product_category: str) -> str:
        """Generate a reason for why this template is suggested."""
        reasons = {
            "studio-white": "Clean background ideal for e-commerce listings",
            "lifestyle-desk": "Shows product in a relatable workspace context",
            "lifestyle-bathroom": "Perfect for beauty and skincare products",
            "lifestyle-kitchen": "Ideal for food and kitchen products",
            "premium-dark": "Creates a luxury, high-end appearance",
            "outdoor-nature": "Emphasizes natural or eco-friendly qualities",
            "ecommerce-amazon": "Meets marketplace image requirements",
        }
        return reasons.get(template["id"], f"Complements {product_category} products well")


# Singleton instance
scene_generator = SceneGenerator()
