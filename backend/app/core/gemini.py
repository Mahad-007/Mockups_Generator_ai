"""Gemini API client for image analysis and generation."""
import google.generativeai as genai
from google.generativeai import types
from PIL import Image
import io
import base64
import json
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Gemini API interactions."""

    def __init__(self):
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set - AI features will not work")
            self._configured = False
            return

        genai.configure(api_key=settings.gemini_api_key)
        self._configured = True

        # Use Gemini 2.0 Flash for both vision and generation
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    @property
    def is_configured(self) -> bool:
        return self._configured

    async def analyze_product(self, image: Image.Image) -> dict:
        """
        Analyze a product image to detect category and attributes.

        Returns dict with: category, attributes, suggested_scenes
        """
        if not self._configured:
            return self._default_analysis()

        try:
            prompt = """Analyze this product image and respond with ONLY valid JSON (no markdown):
{
    "category": "one of: electronics, beauty, food, fashion, home, fitness, other",
    "attributes": {
        "primary_color": "main color",
        "material": "apparent material",
        "style": "modern/classic/minimal/other"
    },
    "suggested_scenes": ["scene1", "scene2", "scene3"]
}

For suggested_scenes, choose from: studio-white, lifestyle-desk, lifestyle-kitchen, outdoor-nature, premium-marble"""

            response = self.model.generate_content([prompt, image])

            # Parse JSON response
            text = response.text.strip()
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            return json.loads(text)

        except Exception as e:
            logger.error(f"Product analysis failed: {e}")
            return self._default_analysis()

    async def generate_scene_image(
        self,
        scene_prompt: str,
        product_image: Optional[Image.Image] = None,
    ) -> Optional[Image.Image]:
        """
        Generate a scene background image using Gemini.

        Note: Gemini 2.0 Flash Experimental supports image generation.
        """
        if not self._configured:
            logger.warning("Gemini not configured, cannot generate scene")
            return None

        try:
            # Enhanced prompt for scene generation
            full_prompt = f"""Generate a high-quality product photography background scene.

Scene: {scene_prompt}

Requirements:
- Professional product photography quality
- Clean, well-lit environment
- Leave clear central space for product placement
- Soft, diffused lighting
- High resolution, sharp details

Generate this scene as an image."""

            response = self.model.generate_content(
                full_prompt,
                generation_config=types.GenerationConfig(
                    response_mime_type="image/png",
                )
            )

            # Extract image from response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        return Image.open(io.BytesIO(image_data))

            logger.warning("No image in Gemini response")
            return None

        except Exception as e:
            logger.error(f"Scene generation failed: {e}")
            return None

    async def generate_mockup(
        self,
        product_image: Image.Image,
        scene_description: str,
    ) -> Optional[Image.Image]:
        """
        Generate a complete mockup with product in scene.

        Uses Gemini's multimodal capabilities to create the final mockup.
        """
        if not self._configured:
            return None

        try:
            prompt = f"""Create a professional product mockup image.

Take this product and place it naturally in this scene: {scene_description}

Requirements:
- Product should be the clear focal point
- Natural lighting and shadows
- Professional product photography style
- The product should look like it belongs in the scene
- Maintain product proportions and details

Generate the final mockup image."""

            response = self.model.generate_content(
                [prompt, product_image],
                generation_config=types.GenerationConfig(
                    response_mime_type="image/png",
                )
            )

            # Extract image from response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        return Image.open(io.BytesIO(image_data))

            return None

        except Exception as e:
            logger.error(f"Mockup generation failed: {e}")
            return None

    def _default_analysis(self) -> dict:
        """Return default analysis when API is unavailable."""
        return {
            "category": "other",
            "attributes": {
                "primary_color": "unknown",
                "material": "unknown",
                "style": "modern"
            },
            "suggested_scenes": ["studio-white", "lifestyle-desk", "premium-marble"]
        }


# Singleton instance
gemini_client = GeminiClient()
