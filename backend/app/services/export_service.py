"""
Export service for mockup exports with platform optimization.

Handles:
- Single mockup exports with presets
- Batch exports to ZIP files
- Platform-specific optimization
"""
import io
import zipfile
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from PIL import Image

from app.core.storage import get_image, storage_service
from app.core.export_optimizer import export_optimizer, EXPORT_PRESETS
from app.core.batch_queue import batch_queue
from app.config import settings


class ExportService:
    """Service for exporting mockups in various formats and sizes."""

    def __init__(self):
        self.optimizer = export_optimizer
        self.queue = batch_queue

    def get_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get all available export presets."""
        return self.optimizer.get_presets()

    def get_presets_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get presets organized by category."""
        categories = {
            "social": [],
            "ecommerce": [],
            "website": [],
            "print": [],
        }

        category_mapping = {
            "instagram-post": "social",
            "instagram-story": "social",
            "instagram-reel-cover": "social",
            "facebook-ad": "social",
            "facebook-post": "social",
            "twitter-post": "social",
            "linkedin-post": "social",
            "pinterest": "social",
            "amazon-main": "ecommerce",
            "amazon-lifestyle": "ecommerce",
            "amazon-zoom": "ecommerce",
            "shopify-product": "ecommerce",
            "etsy-listing": "ecommerce",
            "ebay-gallery": "ecommerce",
            "website-hero": "website",
            "website-thumbnail": "website",
            "website-banner": "website",
            "print-a4": "print",
            "print-letter": "print",
        }

        presets = self.get_presets()
        for preset_id, preset_data in presets.items():
            category = category_mapping.get(preset_id, "website")
            categories[category].append({
                "id": preset_id,
                **preset_data,
            })

        return categories

    async def export_single(
        self,
        image_path: str,
        preset_id: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: str = "png",
        quality: int = 95,
        background_color: Optional[str] = None,
    ) -> bytes:
        """
        Export a single mockup image.

        Args:
            image_path: Path to the source image
            preset_id: Optional preset ID (overrides width/height)
            width: Custom width
            height: Custom height
            format: Output format (png, jpg, webp)
            quality: Quality for lossy formats
            background_color: Background for JPG transparency

        Returns:
            Image bytes in specified format
        """
        # Load image
        image = get_image(image_path)
        if not image:
            raise ValueError(f"Image not found: {image_path}")

        # Export with optimizer
        return await self.optimizer.export(
            image=image,
            preset_id=preset_id,
            width=width,
            height=height,
            format=format,
            quality=quality,
            background_color=background_color,
        )

    async def export_single_and_save(
        self,
        image_path: str,
        preset_id: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: str = "png",
        quality: int = 95,
        background_color: Optional[str] = None,
    ) -> str:
        """
        Export a single mockup and save to storage.

        Returns:
            Path to saved export file
        """
        image_bytes = await self.export_single(
            image_path=image_path,
            preset_id=preset_id,
            width=width,
            height=height,
            format=format,
            quality=quality,
            background_color=background_color,
        )

        # Save to exports folder
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        preset_suffix = f"_{preset_id}" if preset_id else ""
        filename = f"export_{timestamp}{preset_suffix}.{format}"

        # Ensure exports directory exists
        exports_dir = settings.upload_dir / "exports"
        exports_dir.mkdir(exist_ok=True)

        export_path = f"exports/{filename}"
        full_path = settings.upload_dir / "exports" / filename

        with open(full_path, "wb") as f:
            f.write(image_bytes)

        return export_path

    async def export_batch_to_zip(
        self,
        image_paths: List[str],
        preset_id: Optional[str] = None,
        format: str = "png",
        quality: int = 95,
    ) -> bytes:
        """
        Export multiple mockups as a ZIP file.

        Args:
            image_paths: List of image paths to export
            preset_id: Optional preset to apply to all images
            format: Output format for all images
            quality: Quality for lossy formats

        Returns:
            ZIP file bytes
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i, image_path in enumerate(image_paths):
                try:
                    image_bytes = await self.export_single(
                        image_path=image_path,
                        preset_id=preset_id,
                        format=format,
                        quality=quality,
                    )

                    # Generate filename
                    preset_suffix = f"_{preset_id}" if preset_id else ""
                    filename = f"mockup_{i + 1:03d}{preset_suffix}.{format}"

                    zip_file.writestr(filename, image_bytes)

                except Exception as e:
                    # Log error but continue with other files
                    print(f"Error exporting {image_path}: {e}")
                    continue

        return zip_buffer.getvalue()

    async def export_batch_and_save(
        self,
        image_paths: List[str],
        preset_id: Optional[str] = None,
        format: str = "png",
        quality: int = 95,
    ) -> str:
        """
        Export multiple mockups as ZIP and save to storage.

        Returns:
            Path to saved ZIP file
        """
        zip_bytes = await self.export_batch_to_zip(
            image_paths=image_paths,
            preset_id=preset_id,
            format=format,
            quality=quality,
        )

        # Save to exports folder
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        preset_suffix = f"_{preset_id}" if preset_id else ""
        filename = f"mockups_batch_{timestamp}{preset_suffix}.zip"

        # Ensure exports directory exists
        exports_dir = settings.upload_dir / "exports"
        exports_dir.mkdir(exist_ok=True)

        export_path = f"exports/{filename}"
        full_path = settings.upload_dir / "exports" / filename

        with open(full_path, "wb") as f:
            f.write(zip_bytes)

        return export_path

    async def export_multi_preset(
        self,
        image_path: str,
        preset_ids: List[str],
    ) -> bytes:
        """
        Export a single image to multiple preset formats as ZIP.

        Args:
            image_path: Path to source image
            preset_ids: List of preset IDs to export to

        Returns:
            ZIP file bytes with all exports
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for preset_id in preset_ids:
                try:
                    preset = self.optimizer.get_preset(preset_id)
                    if not preset:
                        continue

                    image_bytes = await self.export_single(
                        image_path=image_path,
                        preset_id=preset_id,
                    )

                    filename = f"{preset.name.replace(' ', '_').lower()}.{preset.format}"
                    zip_file.writestr(filename, image_bytes)

                except Exception as e:
                    print(f"Error exporting preset {preset_id}: {e}")
                    continue

        return zip_buffer.getvalue()

    def get_export_filename(
        self,
        base_name: str,
        preset_id: Optional[str] = None,
        format: str = "png",
    ) -> str:
        """Generate a filename for export."""
        preset_suffix = f"_{preset_id}" if preset_id else ""
        return f"{base_name}{preset_suffix}.{format}"


# Singleton instance
export_service = ExportService()
