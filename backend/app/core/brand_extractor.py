"""Brand extraction service for analyzing logos and websites."""
import logging
from typing import Optional, List, Dict, Any
from PIL import Image
import colorsys
import io
from collections import Counter

logger = logging.getLogger(__name__)


class BrandExtractor:
    """
    Extracts brand DNA from logos, websites, and other visual assets.
    
    Uses color analysis and AI to determine:
    - Color palette (primary, secondary, accent)
    - Brand mood (professional, playful, luxury, etc.)
    - Visual style (modern, classic, tech, organic, etc.)
    - Industry hints
    """
    
    def __init__(self):
        from app.core.gemini import gemini_client
        self.gemini = gemini_client
    
    async def extract_from_logo(self, logo_image: Image.Image) -> Dict[str, Any]:
        """
        Extract brand colors and style from a logo image.
        
        Uses color quantization to find dominant colors and AI analysis
        for mood/style detection.
        """
        result = {
            "colors": {},
            "mood": None,
            "style": None,
            "confidence": 0.6,
        }
        
        try:
            # Extract colors using color quantization
            colors = self._extract_dominant_colors(logo_image, num_colors=6)
            
            if colors:
                # Assign roles to colors based on prominence and contrast
                color_roles = self._assign_color_roles(colors)
                result["colors"] = color_roles
            
            # Use AI to analyze logo style and mood
            if self.gemini.is_configured:
                ai_analysis = await self._analyze_logo_with_ai(logo_image, colors)
                if ai_analysis:
                    result["mood"] = ai_analysis.get("mood")
                    result["style"] = ai_analysis.get("style")
                    result["confidence"] = ai_analysis.get("confidence", 0.7)
            
        except Exception as e:
            logger.error(f"Logo extraction failed: {e}")
        
        return result
    
    async def extract_from_website(self, url: str) -> Dict[str, Any]:
        """
        Extract brand attributes from a website URL.
        
        Note: In production, this would use a headless browser to capture
        the website and analyze its design. For MVP, we use AI to infer
        brand attributes from the URL pattern.
        """
        result = {
            "primary_color": None,
            "secondary_color": None,
            "accent_color": None,
            "color_palette": [],
            "mood": None,
            "style": None,
            "industry": None,
            "confidence": 0.5,
        }
        
        try:
            # Extract domain hints
            industry_hints = self._get_industry_from_url(url)
            if industry_hints:
                result["industry"] = industry_hints
            
            # Use AI to analyze the website concept
            if self.gemini.is_configured:
                ai_result = await self._analyze_website_with_ai(url)
                if ai_result:
                    result.update({
                        k: v for k, v in ai_result.items() if v is not None
                    })
                    result["confidence"] = 0.6
            
        except Exception as e:
            logger.error(f"Website extraction failed: {e}")
        
        return result
    
    async def analyze_brand_mood(
        self,
        brand_data: Dict[str, Any],
        brand_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Use AI to analyze and refine brand mood based on extracted data.
        
        Takes existing extracted data and enhances it with AI analysis.
        """
        if not self.gemini.is_configured:
            return {}
        
        try:
            import json
            
            # Build analysis prompt
            prompt = f"""Analyze this brand data and determine the brand's personality.

Brand Name: {brand_name or "Unknown"}
Extracted Colors:
- Primary: {brand_data.get('primary_color', 'not detected')}
- Secondary: {brand_data.get('secondary_color', 'not detected')}
- Accent: {brand_data.get('accent_color', 'not detected')}
Current Mood Guess: {brand_data.get('mood', 'unknown')}
Current Style Guess: {brand_data.get('style', 'unknown')}

Based on these colors and any brand name hints, respond with ONLY valid JSON:
{{
    "mood": "one of: professional, playful, luxury, minimal, bold, elegant, casual, tech, organic, vintage",
    "style": "one of: modern, classic, tech, organic, vintage, minimalist, maximalist, industrial, bohemian, scandinavian",
    "industry": "best guess: tech, beauty, food, fashion, home, fitness, jewelry, electronics, health, lifestyle, other",
    "target_audience": "brief description of likely target audience",
    "confidence": 0.0-1.0
}}

Consider:
- Dark colors often indicate luxury/professional
- Bright colors suggest playful/energetic
- Muted earth tones suggest organic/natural
- High contrast indicates bold/modern
- Pastels suggest soft/feminine"""

            response = self.gemini.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse JSON response
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Brand mood analysis failed: {e}")
            return {}
    
    def _extract_dominant_colors(
        self,
        image: Image.Image,
        num_colors: int = 6,
    ) -> List[str]:
        """
        Extract dominant colors from an image using quantization.
        
        Returns list of hex colors sorted by dominance.
        """
        try:
            # Convert to RGB if necessary
            if image.mode != "RGB":
                # Handle RGBA by compositing on white background
                if image.mode == "RGBA":
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[3])
                    image = background
                else:
                    image = image.convert("RGB")
            
            # Resize for faster processing
            image = image.copy()
            image.thumbnail((200, 200))
            
            # Quantize to get dominant colors
            quantized = image.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
            palette = quantized.getpalette()[:num_colors * 3]
            
            # Count pixel occurrences for each color
            pixels = list(quantized.getdata())
            color_counts = Counter(pixels)
            
            # Get colors sorted by frequency
            colors = []
            for color_idx, count in color_counts.most_common(num_colors):
                if color_idx < num_colors:
                    r = palette[color_idx * 3]
                    g = palette[color_idx * 3 + 1]
                    b = palette[color_idx * 3 + 2]
                    
                    # Skip near-white and near-black colors
                    if not self._is_neutral_color(r, g, b):
                        hex_color = f"#{r:02X}{g:02X}{b:02X}"
                        colors.append(hex_color)
            
            return colors[:num_colors]
            
        except Exception as e:
            logger.error(f"Color extraction failed: {e}")
            return []
    
    def _is_neutral_color(self, r: int, g: int, b: int, threshold: int = 30) -> bool:
        """Check if a color is near-white, near-black, or gray."""
        # Near white
        if r > 240 and g > 240 and b > 240:
            return True
        # Near black
        if r < 15 and g < 15 and b < 15:
            return True
        # Gray (all channels similar)
        if max(abs(r - g), abs(g - b), abs(r - b)) < threshold:
            avg = (r + g + b) / 3
            if avg < 30 or avg > 225:
                return True
        return False
    
    def _assign_color_roles(self, colors: List[str]) -> Dict[str, Any]:
        """
        Assign color roles (primary, secondary, accent) based on visual properties.
        
        Primary: Most prominent non-neutral color
        Secondary: Complementary or contrasting color
        Accent: Most vibrant/saturated remaining color
        """
        result = {
            "primary_color": None,
            "secondary_color": None,
            "accent_color": None,
            "color_palette": colors,
        }
        
        if not colors:
            return result
        
        # Convert to HSV for analysis
        hsv_colors = []
        for hex_color in colors:
            r = int(hex_color[1:3], 16) / 255
            g = int(hex_color[3:5], 16) / 255
            b = int(hex_color[5:7], 16) / 255
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hsv_colors.append((hex_color, h, s, v))
        
        # Primary: First color (most prominent)
        result["primary_color"] = colors[0]
        
        # Find secondary: different hue from primary
        primary_hue = hsv_colors[0][1]
        for hex_color, h, s, v in hsv_colors[1:]:
            hue_diff = min(abs(h - primary_hue), 1 - abs(h - primary_hue))
            if hue_diff > 0.15 and s > 0.2:  # Different hue and not too desaturated
                result["secondary_color"] = hex_color
                break
        
        # If no secondary found, use second color
        if not result["secondary_color"] and len(colors) > 1:
            result["secondary_color"] = colors[1]
        
        # Accent: Most saturated remaining color
        remaining = [c for c in hsv_colors if c[0] not in [result["primary_color"], result["secondary_color"]]]
        if remaining:
            most_saturated = max(remaining, key=lambda x: x[2])  # Sort by saturation
            result["accent_color"] = most_saturated[0]
        elif len(colors) > 2:
            result["accent_color"] = colors[2]
        
        return result
    
    async def _analyze_logo_with_ai(
        self,
        logo_image: Image.Image,
        extracted_colors: List[str],
    ) -> Optional[Dict[str, Any]]:
        """Use Gemini to analyze logo style and mood."""
        try:
            import json
            
            color_info = ", ".join(extracted_colors[:3]) if extracted_colors else "not detected"
            
            prompt = f"""Analyze this logo image to determine brand personality.

Detected colors: {color_info}

Respond with ONLY valid JSON:
{{
    "mood": "one of: professional, playful, luxury, minimal, bold, elegant, casual, tech, organic, vintage",
    "style": "one of: modern, classic, tech, organic, vintage, minimalist, maximalist",
    "confidence": 0.0-1.0
}}

Consider:
- Shape complexity (simple = modern/minimal, complex = classic/detailed)
- Color saturation (high = bold/playful, low = elegant/professional)
- Typography hints if visible
- Overall composition"""

            response = self.gemini.model.generate_content([prompt, logo_image])
            text = response.text.strip()
            
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"AI logo analysis failed: {e}")
            return None
    
    async def _analyze_website_with_ai(self, url: str) -> Optional[Dict[str, Any]]:
        """Use AI to infer brand attributes from website URL."""
        try:
            import json
            
            prompt = f"""Based on this website URL, infer likely brand attributes.
            
URL: {url}

Consider:
- Domain name hints (tech terms, industry keywords)
- TLD (.io for tech, .beauty for cosmetics, etc.)
- Common naming patterns

Respond with ONLY valid JSON:
{{
    "mood": "one of: professional, playful, luxury, minimal, bold, elegant, casual, tech, organic, vintage, or null if uncertain",
    "style": "one of: modern, classic, tech, organic, vintage, minimalist, or null",
    "industry": "one of: tech, beauty, food, fashion, home, fitness, jewelry, electronics, health, lifestyle, other",
    "primary_color": "suggested hex color based on industry norms, or null",
    "confidence": 0.0-1.0 (lower since we're just guessing from URL)
}}"""

            response = self.gemini.model.generate_content(prompt)
            text = response.text.strip()
            
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"AI website analysis failed: {e}")
            return None
    
    def _get_industry_from_url(self, url: str) -> Optional[str]:
        """Extract industry hints from URL patterns."""
        url_lower = url.lower()
        
        industry_keywords = {
            "tech": ["tech", "app", "software", "digital", "ai", "cloud", "data"],
            "beauty": ["beauty", "cosmetic", "skin", "makeup", "hair", "spa"],
            "food": ["food", "eat", "restaurant", "cafe", "kitchen", "cook", "recipe"],
            "fashion": ["fashion", "style", "wear", "cloth", "apparel", "boutique"],
            "fitness": ["fit", "gym", "workout", "sport", "health", "wellness"],
            "home": ["home", "house", "decor", "furniture", "living", "interior"],
            "jewelry": ["jewel", "gold", "silver", "diamond", "ring", "watch"],
        }
        
        for industry, keywords in industry_keywords.items():
            if any(kw in url_lower for kw in keywords):
                return industry
        
        # Check TLD
        if ".io" in url_lower or ".dev" in url_lower or ".ai" in url_lower:
            return "tech"
        
        return None


# Singleton instance
brand_extractor = BrandExtractor()

