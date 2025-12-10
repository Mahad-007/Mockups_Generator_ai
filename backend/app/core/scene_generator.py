"""Scene templates and generation logic."""
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum


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
