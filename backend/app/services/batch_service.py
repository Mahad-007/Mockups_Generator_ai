"""
Batch generation service for creating multiple mockup variations.

Handles:
- Parallel mockup generation
- Variation generation (angles, lighting, backgrounds, styles)
- Progress tracking
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.batch_queue import batch_queue, BatchJob, JobStatus
from app.core.storage import get_image, save_image
from app.core.gemini import gemini_client
from app.core.scene_generator import get_template, get_all_templates, build_customized_prompt
from app.models import Product, Mockup


@dataclass
class VariationConfig:
    """Configuration for generating variations."""
    angles: List[str]
    lighting: List[str]
    backgrounds: List[str]
    styles: List[str]


# Default variation presets
DEFAULT_VARIATIONS = VariationConfig(
    angles=["front", "45-degree", "side"],
    lighting=["soft-diffused", "dramatic", "natural-window"],
    backgrounds=["studio-white", "studio-gray", "lifestyle-desk"],
    styles=["minimal", "lifestyle", "premium"],
)

# Variation configurations for different generation modes
VARIATION_PRESETS = {
    "quick": VariationConfig(
        angles=["front"],
        lighting=["soft-diffused"],
        backgrounds=["studio-white", "lifestyle-desk"],
        styles=["minimal"],
    ),
    "standard": VariationConfig(
        angles=["front", "45-degree"],
        lighting=["soft-diffused", "natural-window"],
        backgrounds=["studio-white", "studio-gray", "lifestyle-desk"],
        styles=["minimal", "lifestyle"],
    ),
    "comprehensive": VariationConfig(
        angles=["front", "45-degree", "side", "top-down"],
        lighting=["soft-diffused", "dramatic", "natural-window", "golden-hour"],
        backgrounds=["studio-white", "studio-gray", "studio-gradient", "lifestyle-desk", "lifestyle-kitchen"],
        styles=["minimal", "lifestyle", "premium", "e-commerce"],
    ),
}


class BatchGenerationService:
    """Service for batch mockup generation with variations."""

    def __init__(self):
        self.queue = batch_queue

    async def generate_single_variation(
        self,
        product: Product,
        scene_template_id: str,
        customization: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Generate a single mockup variation.

        Returns dict with mockup_path and generation details.
        """
        # Get template
        template = get_template(scene_template_id)
        if not template:
            template = get_template("studio-white")

        # Build customized prompt
        scene_prompt = build_customized_prompt(template.id, customization)

        # Load product image
        image_path = product.processed_image_path or product.original_image_path
        product_image = get_image(image_path)

        # Generate with AI
        mockup_image = await gemini_client.generate_mockup(
            product_image=product_image,
            scene_description=scene_prompt,
        )

        if not mockup_image:
            raise Exception("Failed to generate mockup image")

        # Save mockup
        mockup_path = save_image(mockup_image, "mockups")

        return {
            "image_path": mockup_path,
            "scene_template_id": scene_template_id,
            "prompt_used": scene_prompt,
            "customization": customization,
        }

    def create_variation_combinations(
        self,
        base_template_id: str,
        variation_config: VariationConfig,
        max_variations: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Create variation combinations based on config.

        Returns list of (template_id, customization) tuples.
        """
        combinations = []

        # Generate combinations prioritizing diversity
        for angle in variation_config.angles:
            for lighting in variation_config.lighting:
                for bg in variation_config.backgrounds:
                    if len(combinations) >= max_variations:
                        break
                    combinations.append({
                        "template_id": bg,
                        "customization": {
                            "angle": angle,
                            "lighting": lighting,
                        },
                    })
                if len(combinations) >= max_variations:
                    break
            if len(combinations) >= max_variations:
                break

        return combinations

    async def start_batch_generation(
        self,
        db: AsyncSession,
        product_id: str,
        scene_template_ids: Optional[List[str]] = None,
        variation_preset: str = "standard",
        max_variations: int = 10,
        custom_variations: Optional[List[Dict[str, Any]]] = None,
    ) -> BatchJob:
        """
        Start a batch generation job.

        Args:
            db: Database session
            product_id: Product to generate mockups for
            scene_template_ids: Specific templates to use (optional)
            variation_preset: One of quick/standard/comprehensive
            max_variations: Maximum number of variations to generate
            custom_variations: Custom variation configs (overrides preset)

        Returns:
            BatchJob that can be tracked for progress
        """
        # Get product
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Build variation list
        if custom_variations:
            variations = custom_variations[:max_variations]
        elif scene_template_ids:
            # Use specific templates with default customization
            variations = [
                {"template_id": tid, "customization": {}}
                for tid in scene_template_ids[:max_variations]
            ]
        else:
            # Generate variations based on preset
            config = VARIATION_PRESETS.get(variation_preset, VARIATION_PRESETS["standard"])
            variations = self.create_variation_combinations(
                "studio-white",
                config,
                max_variations,
            )

        # Create job
        job = self.queue.create_job(
            job_type="batch_generation",
            total_items=len(variations),
            metadata={
                "product_id": product_id,
                "variation_preset": variation_preset,
            },
        )

        # Define processor function that captures product
        async def process_variation(variation: Dict[str, Any]) -> Dict[str, Any]:
            return await self.generate_single_variation(
                product=product,
                scene_template_id=variation["template_id"],
                customization=variation.get("customization", {}),
            )

        # Start job in background
        self.queue.start_job_async(job.id, variations, process_variation)

        return job

    async def save_completed_mockups(
        self,
        db: AsyncSession,
        job: BatchJob,
        product_id: str,
    ) -> List[Mockup]:
        """
        Save completed mockups from a batch job to database.

        Call this after job completes to persist results.
        """
        mockups = []

        for result in job.results:
            if not result.success or not result.result:
                continue

            data = result.result
            mockup = Mockup(
                product_id=product_id,
                image_path=data["image_path"],
                scene_template_id=data.get("scene_template_id"),
                prompt_used=data.get("prompt_used"),
                generation_params={
                    "batch_job_id": job.id,
                    "customization": data.get("customization"),
                },
            )
            db.add(mockup)
            mockups.append(mockup)

        if mockups:
            await db.flush()
            for mockup in mockups:
                await db.refresh(mockup)

        return mockups

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a batch job."""
        job = self.queue.get_job(job_id)
        if not job:
            return None
        return job.to_dict()

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running batch job."""
        return await self.queue.cancel_job(job_id)


# Singleton instance
batch_service = BatchGenerationService()
