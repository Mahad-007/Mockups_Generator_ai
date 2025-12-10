"""Scene templates and generation logic."""
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class SceneCategory(str, Enum):
    STUDIO = "studio"
    LIFESTYLE = "lifestyle"
    OUTDOOR = "outdoor"
    ECOMMERCE = "e-commerce"
    PREMIUM = "premium"
    SEASONAL = "seasonal"
    SOCIAL = "social"


@dataclass
class CustomizationOptions:
    """Available customization options for a scene."""
    colors: List[str] = field(default_factory=list)  # Available background colors
    surfaces: List[str] = field(default_factory=list)  # wood, marble, concrete, etc.
    lighting: List[str] = field(default_factory=list)  # soft, dramatic, natural, etc.
    angles: List[str] = field(default_factory=list)  # front, 45-degree, top-down


@dataclass
class SceneTemplate:
    """Scene template definition."""
    id: str
    name: str
    category: SceneCategory
    prompt: str
    tags: List[str]
    description: str = ""
    customization: CustomizationOptions = field(default_factory=CustomizationOptions)
    is_premium: bool = False
    popularity: int = 0  # For sorting


# Comprehensive scene library - 25+ templates
SCENE_TEMPLATES: Dict[str, SceneTemplate] = {
    # ========== STUDIO SCENES ==========
    "studio-white": SceneTemplate(
        id="studio-white",
        name="Clean White Studio",
        category=SceneCategory.STUDIO,
        prompt="Pure white seamless photography studio background, professional soft box lighting, clean minimal aesthetic, high-key lighting setup, product photography",
        tags=["minimal", "clean", "e-commerce", "professional", "white"],
        description="Classic white background perfect for e-commerce and catalog shots",
        customization=CustomizationOptions(
            lighting=["soft", "bright", "dramatic"],
            angles=["front", "45-degree", "slight-angle"],
        ),
        popularity=100,
    ),
    "studio-gray": SceneTemplate(
        id="studio-gray",
        name="Neutral Gray Studio",
        category=SceneCategory.STUDIO,
        prompt="Neutral gray seamless photography backdrop, professional studio lighting, subtle gradient, clean product photography setup",
        tags=["neutral", "professional", "versatile", "gray"],
        description="Versatile gray backdrop that works with any product color",
        customization=CustomizationOptions(
            colors=["light-gray", "medium-gray", "charcoal"],
            lighting=["soft", "contrasty", "rim-light"],
        ),
        popularity=85,
    ),
    "studio-gradient": SceneTemplate(
        id="studio-gradient",
        name="Soft Gradient",
        category=SceneCategory.STUDIO,
        prompt="Elegant soft gradient background transitioning smoothly, professional studio lighting, modern aesthetic, subtle color transition",
        tags=["modern", "gradient", "elegant", "colorful"],
        description="Modern gradient backgrounds with customizable colors",
        customization=CustomizationOptions(
            colors=["blue-purple", "pink-orange", "teal-blue", "peach-cream", "gray-white"],
            lighting=["soft", "even"],
        ),
        popularity=78,
    ),
    "studio-colored": SceneTemplate(
        id="studio-colored",
        name="Colored Backdrop",
        category=SceneCategory.STUDIO,
        prompt="Bold solid colored photography backdrop, professional lighting, vibrant yet not overpowering, product-focused composition",
        tags=["bold", "colorful", "branding", "vibrant"],
        description="Eye-catching colored backgrounds for brand-focused shots",
        customization=CustomizationOptions(
            colors=["coral", "sage-green", "dusty-blue", "terracotta", "lavender", "mustard"],
            lighting=["soft", "bright"],
        ),
        popularity=72,
    ),
    "studio-textured": SceneTemplate(
        id="studio-textured",
        name="Textured Backdrop",
        category=SceneCategory.STUDIO,
        prompt="Subtle textured photography backdrop, canvas or linen texture, professional lighting, artistic product photography",
        tags=["texture", "artistic", "canvas", "linen"],
        description="Adds depth with subtle texture while keeping focus on product",
        customization=CustomizationOptions(
            colors=["cream", "light-gray", "beige"],
            surfaces=["canvas", "linen", "paper"],
        ),
        popularity=65,
    ),

    # ========== LIFESTYLE SCENES ==========
    "lifestyle-desk": SceneTemplate(
        id="lifestyle-desk",
        name="Modern Workspace",
        category=SceneCategory.LIFESTYLE,
        prompt="Modern minimalist desk setup, clean wooden desk surface, natural window light, plants and minimal accessories, lifestyle product photography, cozy workspace aesthetic",
        tags=["workspace", "desk", "modern", "tech", "office"],
        description="Perfect for tech products, stationery, and office items",
        customization=CustomizationOptions(
            surfaces=["oak-wood", "walnut", "white-laminate", "concrete"],
            lighting=["natural-window", "warm-afternoon", "bright-morning"],
        ),
        popularity=95,
    ),
    "lifestyle-kitchen": SceneTemplate(
        id="lifestyle-kitchen",
        name="Kitchen Counter",
        category=SceneCategory.LIFESTYLE,
        prompt="Clean modern kitchen counter, marble or granite surface, natural light from window, fresh ingredients and plants nearby, lifestyle food photography",
        tags=["kitchen", "food", "cooking", "home", "marble"],
        description="Ideal for food products, kitchenware, and appliances",
        customization=CustomizationOptions(
            surfaces=["white-marble", "black-granite", "butcher-block", "quartz"],
            lighting=["natural", "warm", "bright"],
        ),
        popularity=88,
    ),
    "lifestyle-bathroom": SceneTemplate(
        id="lifestyle-bathroom",
        name="Spa Bathroom",
        category=SceneCategory.LIFESTYLE,
        prompt="Elegant spa-like bathroom setting, white marble vanity, soft natural light, plants and candles, luxury self-care aesthetic, beauty product photography",
        tags=["bathroom", "spa", "beauty", "skincare", "luxury"],
        description="Luxurious setting for beauty and skincare products",
        customization=CustomizationOptions(
            surfaces=["white-marble", "terrazzo", "light-wood"],
            lighting=["soft-natural", "warm-ambient", "bright-clean"],
        ),
        popularity=82,
    ),
    "lifestyle-bedroom": SceneTemplate(
        id="lifestyle-bedroom",
        name="Cozy Bedroom",
        category=SceneCategory.LIFESTYLE,
        prompt="Cozy minimalist bedroom setting, soft white bedding, natural morning light, warm and inviting atmosphere, lifestyle product photography",
        tags=["bedroom", "cozy", "home", "comfort", "sleep"],
        description="Warm setting for home goods, textiles, and wellness products",
        customization=CustomizationOptions(
            colors=["white", "cream", "soft-gray", "blush"],
            lighting=["morning-light", "golden-hour", "soft-diffused"],
        ),
        popularity=75,
    ),
    "lifestyle-living-room": SceneTemplate(
        id="lifestyle-living-room",
        name="Living Room",
        category=SceneCategory.LIFESTYLE,
        prompt="Modern living room setting, comfortable sofa, coffee table, natural light, plants and books, cozy home aesthetic, lifestyle photography",
        tags=["living-room", "home", "cozy", "furniture", "decor"],
        description="Homey setting for decor, books, and lifestyle products",
        customization=CustomizationOptions(
            surfaces=["wood-coffee-table", "marble-side-table", "woven-rug"],
            lighting=["natural", "warm-evening", "bright-day"],
        ),
        popularity=70,
    ),
    "lifestyle-cafe": SceneTemplate(
        id="lifestyle-cafe",
        name="Coffee Shop",
        category=SceneCategory.LIFESTYLE,
        prompt="Cozy coffee shop setting, rustic wooden table, warm ambient lighting, coffee cups and pastries nearby, cafe aesthetic, lifestyle photography",
        tags=["cafe", "coffee", "rustic", "cozy", "food"],
        description="Trendy cafe setting for food, drinks, and lifestyle products",
        customization=CustomizationOptions(
            surfaces=["rustic-wood", "marble-bistro", "concrete"],
            lighting=["warm-ambient", "natural-window", "moody"],
        ),
        popularity=68,
    ),

    # ========== OUTDOOR SCENES ==========
    "outdoor-nature": SceneTemplate(
        id="outdoor-nature",
        name="Natural Outdoor",
        category=SceneCategory.OUTDOOR,
        prompt="Beautiful natural outdoor setting, soft grass or moss surface, dappled sunlight through trees, organic aesthetic, eco-friendly product photography",
        tags=["nature", "outdoor", "organic", "eco", "green"],
        description="Natural setting for eco-friendly and organic products",
        customization=CustomizationOptions(
            surfaces=["grass", "moss", "stone", "wood-stump"],
            lighting=["dappled-sunlight", "golden-hour", "soft-overcast"],
        ),
        popularity=80,
    ),
    "outdoor-beach": SceneTemplate(
        id="outdoor-beach",
        name="Beach Setting",
        category=SceneCategory.OUTDOOR,
        prompt="Beautiful beach setting, soft sand surface, ocean in background, golden hour sunlight, summer vacation aesthetic, lifestyle photography",
        tags=["beach", "summer", "vacation", "sand", "ocean"],
        description="Sunny beach vibes for summer and travel products",
        customization=CustomizationOptions(
            lighting=["golden-hour", "bright-midday", "soft-morning"],
            angles=["eye-level", "low-angle"],
        ),
        popularity=76,
    ),
    "outdoor-urban": SceneTemplate(
        id="outdoor-urban",
        name="Urban Street",
        category=SceneCategory.OUTDOOR,
        prompt="Urban street scene, concrete or brick surface, city atmosphere, modern streetwear aesthetic, urban product photography",
        tags=["urban", "street", "city", "concrete", "modern"],
        description="Edgy urban setting for fashion and streetwear",
        customization=CustomizationOptions(
            surfaces=["concrete", "brick", "asphalt", "metal"],
            lighting=["natural", "dramatic-shadow", "overcast"],
        ),
        popularity=73,
    ),
    "outdoor-garden": SceneTemplate(
        id="outdoor-garden",
        name="Garden Setting",
        category=SceneCategory.OUTDOOR,
        prompt="Beautiful garden setting, flowers and greenery, natural sunlight, fresh and vibrant atmosphere, botanical product photography",
        tags=["garden", "flowers", "botanical", "fresh", "spring"],
        description="Fresh floral setting for beauty and wellness products",
        customization=CustomizationOptions(
            surfaces=["garden-table", "stone-path", "grass"],
            lighting=["bright-natural", "soft-morning", "golden-afternoon"],
        ),
        popularity=71,
    ),

    # ========== E-COMMERCE SCENES ==========
    "ecommerce-amazon": SceneTemplate(
        id="ecommerce-amazon",
        name="Amazon Standard",
        category=SceneCategory.ECOMMERCE,
        prompt="Pure white background, professional product photography, bright even lighting, clean isolated product shot, e-commerce marketplace standard, no shadows",
        tags=["amazon", "e-commerce", "white", "marketplace", "clean"],
        description="Meets Amazon and marketplace image requirements",
        customization=CustomizationOptions(
            lighting=["bright-even", "soft-shadow", "no-shadow"],
        ),
        popularity=98,
        is_premium=False,
    ),
    "ecommerce-lifestyle": SceneTemplate(
        id="ecommerce-lifestyle",
        name="E-commerce Lifestyle",
        category=SceneCategory.ECOMMERCE,
        prompt="Clean lifestyle product photography, simple props, professional lighting, context showing product in use, e-commerce optimized",
        tags=["e-commerce", "lifestyle", "context", "professional"],
        description="Lifestyle shots optimized for online stores",
        customization=CustomizationOptions(
            surfaces=["white-surface", "light-wood", "marble"],
            lighting=["bright", "soft-natural"],
        ),
        popularity=85,
    ),
    "ecommerce-flat-lay": SceneTemplate(
        id="ecommerce-flat-lay",
        name="Flat Lay",
        category=SceneCategory.ECOMMERCE,
        prompt="Professional flat lay photography, top-down view, clean organized arrangement, minimal props, bright even lighting, social media optimized",
        tags=["flat-lay", "top-down", "organized", "social-media"],
        description="Top-down flat lay perfect for social media and catalogs",
        customization=CustomizationOptions(
            surfaces=["white", "marble", "wood", "colored-paper"],
            colors=["white", "pink", "blue", "terracotta"],
        ),
        popularity=82,
    ),

    # ========== PREMIUM SCENES ==========
    "premium-dark": SceneTemplate(
        id="premium-dark",
        name="Dark Luxury",
        category=SceneCategory.PREMIUM,
        prompt="Dark luxury backdrop, dramatic low-key lighting, premium product photography, elegant shadows, high-end aesthetic, moody atmosphere",
        tags=["luxury", "dark", "premium", "dramatic", "moody"],
        description="Dramatic dark setting for luxury and premium products",
        customization=CustomizationOptions(
            colors=["black", "deep-navy", "charcoal"],
            lighting=["dramatic-spot", "rim-light", "soft-moody"],
        ),
        popularity=77,
        is_premium=True,
    ),
    "premium-marble": SceneTemplate(
        id="premium-marble",
        name="Marble Surface",
        category=SceneCategory.PREMIUM,
        prompt="Elegant white marble surface, luxury product photography, soft diffused lighting, premium aesthetic, gold accents optional",
        tags=["marble", "luxury", "elegant", "premium", "white"],
        description="Classic marble elegance for premium products",
        customization=CustomizationOptions(
            surfaces=["white-marble", "black-marble", "green-marble", "pink-marble"],
            lighting=["soft-diffused", "bright-clean", "warm"],
        ),
        popularity=86,
        is_premium=True,
    ),
    "premium-velvet": SceneTemplate(
        id="premium-velvet",
        name="Velvet Luxury",
        category=SceneCategory.PREMIUM,
        prompt="Rich velvet fabric surface, luxury jewelry photography style, dramatic lighting, premium texture, elegant and sophisticated",
        tags=["velvet", "luxury", "jewelry", "rich", "elegant"],
        description="Luxurious velvet for jewelry and premium accessories",
        customization=CustomizationOptions(
            colors=["deep-red", "navy-blue", "emerald", "black", "burgundy"],
            lighting=["dramatic", "soft-spotlight"],
        ),
        popularity=69,
        is_premium=True,
    ),

    # ========== SEASONAL SCENES ==========
    "seasonal-summer": SceneTemplate(
        id="seasonal-summer",
        name="Summer Vibes",
        category=SceneCategory.SEASONAL,
        prompt="Bright summer setting, tropical plants, vibrant colors, sunny atmosphere, summer vacation aesthetic, fresh and energetic",
        tags=["summer", "tropical", "bright", "vacation", "vibrant"],
        description="Bright and fresh summer atmosphere",
        customization=CustomizationOptions(
            colors=["coral", "turquoise", "yellow", "palm-green"],
            lighting=["bright-sunny", "golden-hour"],
        ),
        popularity=74,
    ),
    "seasonal-autumn": SceneTemplate(
        id="seasonal-autumn",
        name="Autumn Warmth",
        category=SceneCategory.SEASONAL,
        prompt="Warm autumn setting, fallen leaves, wooden surface, golden hour lighting, cozy fall aesthetic, warm earth tones",
        tags=["autumn", "fall", "warm", "cozy", "leaves"],
        description="Warm and cozy autumn atmosphere",
        customization=CustomizationOptions(
            colors=["orange", "burgundy", "golden", "brown"],
            surfaces=["rustic-wood", "burlap", "wool"],
        ),
        popularity=72,
    ),
    "seasonal-winter": SceneTemplate(
        id="seasonal-winter",
        name="Winter Cozy",
        category=SceneCategory.SEASONAL,
        prompt="Cozy winter setting, soft white fur or knit textures, warm lighting, hygge aesthetic, holiday feeling, snowy atmosphere",
        tags=["winter", "cozy", "holiday", "snow", "hygge"],
        description="Cozy winter setting perfect for holiday season",
        customization=CustomizationOptions(
            colors=["white", "cream", "silver", "pine-green", "red"],
            surfaces=["faux-fur", "knit", "wood"],
        ),
        popularity=73,
    ),
    "seasonal-spring": SceneTemplate(
        id="seasonal-spring",
        name="Spring Fresh",
        category=SceneCategory.SEASONAL,
        prompt="Fresh spring setting, flowers and greenery, bright natural light, renewal aesthetic, pastel colors, cherry blossoms",
        tags=["spring", "fresh", "flowers", "pastel", "renewal"],
        description="Fresh and vibrant spring atmosphere",
        customization=CustomizationOptions(
            colors=["pastel-pink", "mint-green", "lavender", "soft-yellow"],
            lighting=["bright-natural", "soft-morning"],
        ),
        popularity=71,
    ),

    # ========== SOCIAL MEDIA SCENES ==========
    "social-instagram": SceneTemplate(
        id="social-instagram",
        name="Instagram Ready",
        category=SceneCategory.SOCIAL,
        prompt="Instagram-optimized product photography, trendy aesthetic, perfect composition, influencer style, social media ready, engaging and shareable",
        tags=["instagram", "social-media", "trendy", "influencer"],
        description="Optimized for Instagram engagement",
        customization=CustomizationOptions(
            colors=["millennial-pink", "sage-green", "terracotta", "cream"],
            lighting=["golden-hour", "soft-natural", "ring-light"],
        ),
        popularity=88,
    ),
    "social-pinterest": SceneTemplate(
        id="social-pinterest",
        name="Pinterest Perfect",
        category=SceneCategory.SOCIAL,
        prompt="Pinterest-style product photography, aspirational lifestyle, beautiful composition, save-worthy aesthetic, vertical format optimized",
        tags=["pinterest", "aspirational", "lifestyle", "vertical"],
        description="Designed for Pinterest saves and engagement",
        customization=CustomizationOptions(
            surfaces=["marble", "wood", "linen"],
            lighting=["bright-airy", "soft-natural"],
        ),
        popularity=79,
    ),
}


def get_all_templates() -> List[SceneTemplate]:
    """Get all scene templates sorted by popularity."""
    return sorted(SCENE_TEMPLATES.values(), key=lambda x: x.popularity, reverse=True)


def get_templates_by_category(category: SceneCategory) -> List[SceneTemplate]:
    """Get templates filtered by category."""
    return [t for t in get_all_templates() if t.category == category]


def get_template(template_id: str) -> Optional[SceneTemplate]:
    """Get a single template by ID."""
    return SCENE_TEMPLATES.get(template_id)


def search_templates(query: str) -> List[SceneTemplate]:
    """Search templates by name, tags, or description."""
    query = query.lower()
    results = []
    for template in SCENE_TEMPLATES.values():
        # Search in name, tags, and description
        if (query in template.name.lower() or
            query in template.description.lower() or
            any(query in tag for tag in template.tags)):
            results.append(template)
    return sorted(results, key=lambda x: x.popularity, reverse=True)


def get_categories() -> List[str]:
    """Get all unique categories."""
    return [c.value for c in SceneCategory]


def build_customized_prompt(template_id: str, customizations: Dict) -> str:
    """
    Build a customized prompt based on template and user selections.

    Args:
        template_id: The base template ID
        customizations: Dict with keys like 'color', 'surface', 'lighting', 'angle'

    Returns:
        Customized prompt string
    """
    template = get_template(template_id)
    if not template:
        return ""

    prompt = template.prompt

    # Apply customizations
    if customizations.get("color"):
        prompt += f", {customizations['color']} color scheme"

    if customizations.get("surface"):
        prompt += f", {customizations['surface']} surface"

    if customizations.get("lighting"):
        prompt += f", {customizations['lighting']} lighting"

    if customizations.get("angle"):
        prompt += f", {customizations['angle']} camera angle"

    return prompt


# ---------- Context-aware suggestions (Phase 6) ----------

# Category-driven starter sets
CATEGORY_PRIORITIES: Dict[str, List[str]] = {
    "electronics": ["lifestyle-desk", "studio-gray", "premium-dark", "ecommerce-amazon", "social-instagram"],
    "tech": ["lifestyle-desk", "studio-gray", "premium-dark", "ecommerce-amazon"],
    "beauty": ["lifestyle-bathroom", "premium-marble", "social-instagram", "studio-gradient"],
    "beauty/skincare": ["lifestyle-bathroom", "premium-marble", "social-instagram", "studio-gradient"],
    "food": ["lifestyle-kitchen", "lifestyle-cafe", "outdoor-nature", "ecommerce-flat-lay"],
    "food/beverage": ["lifestyle-kitchen", "lifestyle-cafe", "outdoor-nature", "ecommerce-flat-lay"],
    "fashion": ["outdoor-urban", "studio-colored", "social-instagram", "premium-dark"],
    "fashion/apparel": ["outdoor-urban", "studio-colored", "social-instagram"],
    "home": ["lifestyle-living-room", "lifestyle-bedroom", "studio-white", "social-pinterest"],
    "home/furniture": ["lifestyle-living-room", "lifestyle-bedroom", "studio-white"],
    "fitness": ["outdoor-nature", "studio-white", "outdoor-urban", "lifestyle-desk"],
    "sports/fitness": ["outdoor-nature", "studio-white", "outdoor-urban"],
    "other": ["studio-white", "lifestyle-desk", "ecommerce-amazon", "social-instagram"],
}

# Style and mood driven helpers
STYLE_SCENE_MAP: Dict[str, List[str]] = {
    "premium": ["premium-marble", "premium-dark", "premium-velvet"],
    "luxury": ["premium-marble", "premium-dark", "premium-velvet"],
    "minimal": ["studio-white", "studio-gray", "lifestyle-desk"],
    "modern": ["studio-gradient", "studio-colored", "lifestyle-desk"],
    "classic": ["studio-textured", "premium-marble"],
    "playful": ["studio-colored", "social-instagram", "outdoor-nature"],
}

# Color harmony nudges
COLOR_SCENE_MAP: Dict[str, List[str]] = {
    "dark": ["studio-white", "studio-gradient", "premium-marble"],
    "light": ["premium-dark", "studio-gradient"],
    "warm": ["studio-colored", "seasonal-autumn", "seasonal-summer"],
    "cool": ["studio-gray", "outdoor-nature", "studio-gradient"],
}

# Trending/seasonal awareness
TRENDING_BY_CATEGORY: Dict[str, List[str]] = {
    "electronics": ["lifestyle-desk", "premium-dark"],
    "beauty": ["lifestyle-bathroom", "premium-marble"],
    "food": ["lifestyle-kitchen", "ecommerce-flat-lay"],
    "fashion": ["outdoor-urban", "studio-colored"],
    "home": ["lifestyle-living-room", "social-pinterest"],
    "fitness": ["outdoor-nature", "studio-white"],
}

SEASONAL_SCENES: Dict[str, List[str]] = {
    "winter": ["seasonal-winter", "premium-dark"],
    "spring": ["seasonal-spring", "outdoor-garden"],
    "summer": ["seasonal-summer", "outdoor-beach"],
    "autumn": ["seasonal-autumn", "studio-textured"],
}

DEFAULT_SCENES = ["studio-white", "lifestyle-desk", "ecommerce-amazon", "social-instagram"]


def normalize_category(category: Optional[str]) -> str:
    """Normalize category strings to canonical keys."""
    if not category:
        return "other"
    c = category.lower()
    aliases = {
        "tech": "electronics",
        "electronics/tech": "electronics",
        "beauty/skincare": "beauty",
        "food/beverage": "food",
        "fashion/apparel": "fashion",
        "home/furniture": "home",
        "sports/fitness": "fitness",
    }
    return aliases.get(c, c)


def _detect_season(now: Optional[datetime] = None) -> Optional[str]:
    """Return current season name to influence seasonal suggestions."""
    now = now or datetime.utcnow()
    month = now.month
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    if month in (9, 10, 11):
        return "autumn"
    return None


def _color_profile(color: Optional[str]) -> Optional[str]:
    if not color:
        return None
    color = color.lower()
    if any(term in color for term in ["black", "charcoal", "navy", "dark"]):
        return "dark"
    if any(term in color for term in ["white", "cream", "beige", "silver", "light"]):
        return "light"
    if any(term in color for term in ["red", "orange", "yellow", "coral", "gold"]):
        return "warm"
    if any(term in color for term in ["blue", "teal", "green", "mint"]):
        return "cool"
    return None


def _candidate_scene_ids(
    normalized_category: str,
    attributes: Dict,
    brand_context: Dict,
    season: Optional[str],
) -> List[str]:
    candidates = []

    # Category seed
    if normalized_category in CATEGORY_PRIORITIES:
        candidates.extend(CATEGORY_PRIORITIES[normalized_category])

    # Style/mood
    style = (attributes.get("style") or "").lower()
    if style and style in STYLE_SCENE_MAP:
        candidates.extend(STYLE_SCENE_MAP[style])

    mood = (brand_context.get("mood") or "").lower()
    if mood and mood in STYLE_SCENE_MAP:
        candidates.extend(STYLE_SCENE_MAP[mood])

    # Color harmony
    color_profile = _color_profile(attributes.get("primary_color"))
    if color_profile and color_profile in COLOR_SCENE_MAP:
        candidates.extend(COLOR_SCENE_MAP[color_profile])

    # Brand-suggested scenes
    brand_suggestions = brand_context.get("suggested_scenes") or []
    candidates.extend(brand_suggestions)

    # Seasonal boost
    if season and season in SEASONAL_SCENES:
        candidates.extend(SEASONAL_SCENES[season])

    # Trending
    if normalized_category in TRENDING_BY_CATEGORY:
        candidates.extend(TRENDING_BY_CATEGORY[normalized_category])

    # Defaults
    candidates.extend(DEFAULT_SCENES)

    # Keep order but remove duplicates
    seen = set()
    ordered = []
    for cid in candidates:
        if cid not in seen:
            seen.add(cid)
            ordered.append(cid)
    return ordered


def _score_template(
    template: SceneTemplate,
    normalized_category: str,
    attributes: Dict,
    brand_context: Dict,
    season: Optional[str],
    index_hint: int,
) -> Tuple[float, List[Dict], bool, Optional[str]]:
    """Compute a relevance score and reasons for a template."""
    reasons: List[Dict] = []
    score = template.popularity / 120  # base influence from curated popularity

    # Category fit
    cat_list = CATEGORY_PRIORITIES.get(normalized_category, [])
    if template.id in cat_list:
        cat_weight = max(0.25, 0.5 - (0.05 * cat_list.index(template.id)))
        score += cat_weight
        reasons.append({"label": "Category match", "detail": f"Strong fit for {normalized_category} products"})

    # Attribute/style fit
    style = (attributes.get("style") or "").lower()
    if style and template.id in STYLE_SCENE_MAP.get(style, []):
        score += 0.15
        reasons.append({"label": "Style alignment", "detail": f"Matches {style} aesthetic"})

    # Color harmony
    color_profile = _color_profile(attributes.get("primary_color"))
    if color_profile and template.id in COLOR_SCENE_MAP.get(color_profile, []):
        score += 0.12
        reasons.append({"label": "Color harmony", "detail": f"Balances {color_profile} colored products"})

    # Brand alignment
    brand_scenes = brand_context.get("suggested_scenes") or []
    if template.id in brand_scenes:
        score += 0.18
        reasons.append({"label": "Brand alignment", "detail": "Matches brand mood/style preferences"})
    elif brand_context.get("industry") and template.category in [SceneCategory.PREMIUM, SceneCategory.SOCIAL]:
        score += 0.05

    # Trending boost
    trending_list = TRENDING_BY_CATEGORY.get(normalized_category, [])
    trending = template.id in trending_list
    if trending:
        score += 0.1
        reasons.append({"label": "Trending", "detail": "Popular in your product category right now"})

    # Seasonal boost
    seasonal_match = None
    if season and template.id in SEASONAL_SCENES.get(season, []):
        seasonal_match = season
        score += 0.08
        reasons.append({"label": "Seasonal", "detail": f"Works well for {season} campaigns"})

    # Distance penalty to keep ordering meaningful
    score -= min(index_hint * 0.01, 0.1)

    # Normalize
    relevance = max(0.05, min(1.0, round(score, 2)))
    return relevance, reasons, trending, seasonal_match


def build_scene_suggestions(
    product_category: Optional[str],
    attributes: Optional[Dict] = None,
    brand_context: Optional[Dict] = None,
    limit: int = 6,
) -> List[Dict]:
    """
    Build ranked scene suggestions using product + brand context.
    """
    attributes = attributes or {}
    brand_context = brand_context or {}
    normalized_category = normalize_category(product_category or attributes.get("category"))
    season = _detect_season()

    candidate_ids = _candidate_scene_ids(normalized_category, attributes, brand_context, season)

    suggestions = []
    for idx, scene_id in enumerate(candidate_ids):
        template = get_template(scene_id)
        if not template:
            continue

        relevance, reasons, trending, seasonal_match = _score_template(
            template,
            normalized_category,
            attributes,
            brand_context,
            season,
            idx,
        )

        suggestions.append({
            "template": template,
            "relevance": relevance,
            "reasons": reasons,
            "trending": trending,
            "seasonal": seasonal_match,
            "feedback_token": f"{scene_id}:{normalized_category}",
        })

    # Sort by relevance then popularity
    suggestions = sorted(
        suggestions,
        key=lambda s: (s["relevance"], s["template"].popularity),
        reverse=True,
    )

    return suggestions[:limit]
