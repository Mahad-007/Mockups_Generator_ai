from PIL import Image
import io
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class ExportPreset:
    name: str
    width: int
    height: int
    format: str = "png"
    quality: int = 95
    background_color: Optional[str] = None  # For JPG exports


# Platform-specific presets
EXPORT_PRESETS = {
    # Instagram
    "instagram-post": ExportPreset("Instagram Post", 1080, 1080),
    "instagram-story": ExportPreset("Instagram Story", 1080, 1920),
    "instagram-reel-cover": ExportPreset("Instagram Reel Cover", 1080, 1920),

    # Amazon
    "amazon-main": ExportPreset("Amazon Main", 1000, 1000, background_color="#FFFFFF"),
    "amazon-lifestyle": ExportPreset("Amazon Lifestyle", 1500, 1500),
    "amazon-zoom": ExportPreset("Amazon Zoom", 2000, 2000),

    # Website
    "website-hero": ExportPreset("Website Hero", 1920, 1080),
    "website-thumbnail": ExportPreset("Website Thumbnail", 400, 400),
    "website-banner": ExportPreset("Website Banner", 1200, 400),

    # Social Media
    "facebook-ad": ExportPreset("Facebook Ad", 1200, 628),
    "facebook-post": ExportPreset("Facebook Post", 1200, 630),
    "twitter-post": ExportPreset("Twitter Post", 1200, 675),
    "linkedin-post": ExportPreset("LinkedIn Post", 1200, 627),
    "pinterest": ExportPreset("Pinterest", 1000, 1500),

    # Print
    "print-a4": ExportPreset("Print A4 (300dpi)", 2480, 3508, quality=100),
    "print-letter": ExportPreset("Print Letter (300dpi)", 2550, 3300, quality=100),

    # E-commerce
    "shopify-product": ExportPreset("Shopify Product", 2048, 2048),
    "etsy-listing": ExportPreset("Etsy Listing", 2000, 2000),
    "ebay-gallery": ExportPreset("eBay Gallery", 1600, 1600),
}


class ExportOptimizer:
    """Handles exporting mockups in various formats and sizes."""

    def __init__(self):
        self.presets = EXPORT_PRESETS

    def get_presets(self) -> dict:
        """Get all available export presets."""
        return {
            preset_id: {
                "name": preset.name,
                "width": preset.width,
                "height": preset.height,
                "format": preset.format,
            }
            for preset_id, preset in self.presets.items()
        }

    def get_preset(self, preset_id: str) -> Optional[ExportPreset]:
        """Get a specific preset by ID."""
        return self.presets.get(preset_id)

    async def export(
        self,
        image: Image.Image,
        preset_id: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: str = "png",
        quality: int = 95,
        background_color: Optional[str] = None,
    ) -> bytes:
        """
        Export an image with specified settings.

        Args:
            image: PIL Image to export
            preset_id: Optional preset ID (overrides width/height)
            width: Custom width
            height: Custom height
            format: Output format (png, jpg, webp)
            quality: Quality for lossy formats (1-100)
            background_color: Background color for JPG (replaces transparency)

        Returns:
            Image bytes in the specified format
        """
        # Apply preset if provided
        if preset_id:
            preset = self.get_preset(preset_id)
            if preset:
                width = preset.width
                height = preset.height
                format = preset.format
                quality = preset.quality
                background_color = background_color or preset.background_color

        # Resize if dimensions provided
        if width and height:
            image = self._smart_resize(image, width, height)

        # Handle transparency for JPG
        if format.lower() in ["jpg", "jpeg"] and image.mode == "RGBA":
            image = self._flatten_transparency(image, background_color or "#FFFFFF")

        # Export to bytes
        output = io.BytesIO()

        save_kwargs = {}
        if format.lower() in ["jpg", "jpeg"]:
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
            image = image.convert("RGB")
        elif format.lower() == "webp":
            save_kwargs["quality"] = quality
        elif format.lower() == "png":
            save_kwargs["optimize"] = True

        image.save(output, format=format.upper(), **save_kwargs)
        return output.getvalue()

    def _smart_resize(
        self,
        image: Image.Image,
        target_width: int,
        target_height: int,
    ) -> Image.Image:
        """
        Resize image to fit within target dimensions while maintaining aspect ratio.
        Centers the image on a canvas of the target size.
        """
        # Calculate aspect ratios
        img_ratio = image.width / image.height
        target_ratio = target_width / target_height

        # Determine resize dimensions
        if img_ratio > target_ratio:
            # Image is wider - fit to width
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            # Image is taller - fit to height
            new_height = target_height
            new_width = int(target_height * img_ratio)

        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Create canvas and center image
        if image.mode == "RGBA":
            canvas = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
        else:
            canvas = Image.new("RGB", (target_width, target_height), (255, 255, 255))

        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2

        if image.mode == "RGBA":
            canvas.paste(resized, (x, y), resized)
        else:
            canvas.paste(resized, (x, y))

        return canvas

    def _flatten_transparency(
        self,
        image: Image.Image,
        background_color: str,
    ) -> Image.Image:
        """Flatten RGBA image onto solid background color."""
        # Parse hex color
        bg_color = tuple(int(background_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

        # Create background
        background = Image.new("RGB", image.size, bg_color)

        # Composite
        if image.mode == "RGBA":
            background.paste(image, mask=image.split()[3])
        else:
            background.paste(image)

        return background

    async def batch_export(
        self,
        images: List[Image.Image],
        preset_id: str,
    ) -> List[bytes]:
        """Export multiple images with the same preset."""
        results = []
        for image in images:
            result = await self.export(image, preset_id=preset_id)
            results.append(result)
        return results


# Singleton instance
export_optimizer = ExportOptimizer()
