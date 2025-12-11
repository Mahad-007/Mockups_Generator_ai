"""Brand Pydantic schemas for API validation and serialization."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


# Valid mood options
VALID_MOODS = [
    "professional", "playful", "luxury", "minimal", "bold", 
    "elegant", "casual", "tech", "organic", "vintage", "modern"
]

# Valid style options
VALID_STYLES = [
    "modern", "classic", "tech", "organic", "vintage", 
    "minimalist", "maximalist", "industrial", "bohemian", "scandinavian"
]

# Valid industry options
VALID_INDUSTRIES = [
    "tech", "beauty", "food", "fashion", "home", "fitness", 
    "jewelry", "electronics", "health", "lifestyle", "automotive", "other"
]


def validate_hex_color(color: Optional[str]) -> Optional[str]:
    """Validate hex color format."""
    if color is None:
        return None
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        raise ValueError(f"Invalid hex color: {color}. Must be in format #RRGGBB")
    return color.upper()


class BrandBase(BaseModel):
    """Base brand fields."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = None


class BrandCreate(BrandBase):
    """Schema for creating a brand."""
    # Colors
    primary_color: Optional[str] = Field(None, description="Primary brand color in hex (#RRGGBB)")
    secondary_color: Optional[str] = Field(None, description="Secondary brand color in hex (#RRGGBB)")
    accent_color: Optional[str] = Field(None, description="Accent color in hex (#RRGGBB)")
    background_color: Optional[str] = Field(None, description="Background color preference in hex")
    color_palette: Optional[List[str]] = Field(None, description="Additional colors")
    
    # Typography
    primary_font: Optional[str] = None
    secondary_font: Optional[str] = None
    font_style: Optional[str] = None
    
    # Style
    mood: Optional[str] = Field(None, description="Brand mood/tone")
    style: Optional[str] = Field(None, description="Visual style")
    industry: Optional[str] = Field(None, description="Industry category")
    target_audience: Optional[str] = Field(None, max_length=200)
    
    # Preferences
    preferred_lighting: Optional[str] = Field(None, description="Lighting preference for mockups")
    
    # Set as default
    is_default: bool = False
    
    @field_validator('primary_color', 'secondary_color', 'accent_color', 'background_color')
    @classmethod
    def validate_colors(cls, v):
        return validate_hex_color(v)
    
    @field_validator('color_palette')
    @classmethod
    def validate_palette(cls, v):
        if v is None:
            return None
        return [validate_hex_color(c) for c in v]
    
    @field_validator('mood')
    @classmethod
    def validate_mood(cls, v):
        if v is not None and v.lower() not in VALID_MOODS:
            # Allow custom moods but normalize known ones
            return v.lower()
        return v.lower() if v else None
    
    @field_validator('style')
    @classmethod
    def validate_style(cls, v):
        if v is not None:
            return v.lower()
        return None


class BrandUpdate(BaseModel):
    """Schema for updating a brand."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Colors
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    background_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    
    # Typography
    primary_font: Optional[str] = None
    secondary_font: Optional[str] = None
    font_style: Optional[str] = None
    
    # Style
    mood: Optional[str] = None
    style: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    
    # Preferences
    preferred_lighting: Optional[str] = None
    is_default: Optional[bool] = None
    
    @field_validator('primary_color', 'secondary_color', 'accent_color', 'background_color')
    @classmethod
    def validate_colors(cls, v):
        return validate_hex_color(v)


class BrandResponse(BaseModel):
    """Schema for brand API responses."""
    id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    
    # Colors
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    background_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    
    # Typography
    primary_font: Optional[str] = None
    secondary_font: Optional[str] = None
    font_style: Optional[str] = None
    
    # Style
    mood: Optional[str] = None
    style: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    
    # AI-generated
    prompt_description: Optional[str] = None
    suggested_scenes: Optional[List[str]] = None
    preferred_lighting: Optional[str] = None
    
    # Flags
    is_default: bool = False
    is_extracted: bool = False
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BrandExtractRequest(BaseModel):
    """Schema for brand extraction request."""
    website_url: Optional[str] = Field(None, description="URL to analyze for brand style")
    brand_name: Optional[str] = Field(None, description="Brand name to help with analysis")


class BrandExtractResponse(BaseModel):
    """Schema for brand extraction response."""
    extracted: dict = Field(..., description="Extracted brand attributes")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")


class BrandPromptResponse(BaseModel):
    """Schema for brand-influenced prompt generation."""
    brand_id: str
    original_prompt: str
    brand_enhanced_prompt: str
    brand_attributes_applied: dict


class BrandScenesResponse(BaseModel):
    """Schema for brand-suggested scenes."""
    brand_id: str
    brand_mood: Optional[str]
    brand_style: Optional[str]
    suggested_scenes: List[dict]  # [{template_id, reason, relevance}]


