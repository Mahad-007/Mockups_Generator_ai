from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from typing import Optional, Tuple


class Compositor:
    """Handles compositing products onto scene backgrounds."""

    async def composite(
        self,
        product: Image.Image,
        background: Image.Image,
        position: Tuple[int, int] = None,
        scale: float = None,
        add_shadow: bool = True,
        shadow_opacity: float = 0.3,
        shadow_offset: Tuple[int, int] = (10, 10),
        shadow_blur: int = 15,
    ) -> Image.Image:
        """
        Composite a product onto a background scene.

        Args:
            product: Product image with transparent background
            background: Background scene image
            position: (x, y) position for product center. None = centered
            scale: Scale factor for product. None = auto-fit
            add_shadow: Whether to add drop shadow
            shadow_opacity: Shadow opacity (0-1)
            shadow_offset: (x, y) shadow offset
            shadow_blur: Shadow blur radius

        Returns:
            Composited image
        """
        # Ensure RGBA mode
        if product.mode != "RGBA":
            product = product.convert("RGBA")
        if background.mode != "RGBA":
            background = background.convert("RGBA")

        # Calculate scale if not provided
        if scale is None:
            scale = self._calculate_auto_scale(product, background)

        # Resize product
        new_width = int(product.width * scale)
        new_height = int(product.height * scale)
        product = product.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Calculate position if not provided
        if position is None:
            position = (
                (background.width - product.width) // 2,
                (background.height - product.height) // 2,
            )

        # Create result image
        result = background.copy()

        # Add shadow if requested
        if add_shadow:
            shadow = await self._create_shadow(
                product,
                shadow_opacity,
                shadow_offset,
                shadow_blur,
            )
            shadow_pos = (
                position[0] + shadow_offset[0],
                position[1] + shadow_offset[1],
            )
            result.paste(shadow, shadow_pos, shadow)

        # Paste product
        result.paste(product, position, product)

        return result

    def _calculate_auto_scale(
        self,
        product: Image.Image,
        background: Image.Image,
        max_coverage: float = 0.6,
    ) -> float:
        """Calculate scale to fit product nicely in background."""
        # Target: product should cover at most max_coverage of the background
        width_scale = (background.width * max_coverage) / product.width
        height_scale = (background.height * max_coverage) / product.height

        return min(width_scale, height_scale)

    async def _create_shadow(
        self,
        product: Image.Image,
        opacity: float,
        offset: Tuple[int, int],
        blur: int,
    ) -> Image.Image:
        """Create a drop shadow for the product."""
        # Extract alpha channel
        alpha = product.split()[3]

        # Create shadow image (black with product shape)
        shadow = Image.new("RGBA", product.size, (0, 0, 0, 0))
        shadow_alpha = alpha.copy()

        # Apply blur
        shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(radius=blur))

        # Adjust opacity
        shadow_alpha = shadow_alpha.point(lambda x: int(x * opacity))

        # Create shadow with adjusted alpha
        shadow.putalpha(shadow_alpha)

        return shadow

    async def add_reflection(
        self,
        product: Image.Image,
        background: Image.Image,
        reflection_opacity: float = 0.3,
        reflection_height: float = 0.3,
    ) -> Image.Image:
        """
        Add a reflection effect below the product.

        Args:
            product: Product image with transparent background
            background: Background scene image
            reflection_opacity: Opacity of reflection (0-1)
            reflection_height: Height of reflection as fraction of product height

        Returns:
            Image with reflection added
        """
        if product.mode != "RGBA":
            product = product.convert("RGBA")

        # Create flipped reflection
        reflection = product.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        # Crop to desired height
        crop_height = int(reflection.height * reflection_height)
        reflection = reflection.crop((0, 0, reflection.width, crop_height))

        # Create gradient mask for fade effect
        gradient = Image.new("L", reflection.size, 0)
        for y in range(crop_height):
            value = int(255 * (1 - y / crop_height) * reflection_opacity)
            for x in range(reflection.width):
                gradient.putpixel((x, y), value)

        # Apply gradient to reflection alpha
        r, g, b, a = reflection.split()
        a = Image.composite(gradient, Image.new("L", a.size, 0), a)
        reflection.putalpha(a)

        return reflection

    async def match_lighting(
        self,
        product: Image.Image,
        background: Image.Image,
    ) -> Image.Image:
        """
        Adjust product colors to match background lighting.

        Args:
            product: Product image
            background: Background scene to match

        Returns:
            Color-adjusted product image
        """
        # Analyze background average color/brightness
        bg_array = np.array(background.convert("RGB"))
        bg_mean = bg_array.mean(axis=(0, 1))
        bg_brightness = bg_mean.mean() / 255

        # Adjust product brightness to match
        if product.mode != "RGBA":
            product = product.convert("RGBA")

        r, g, b, a = product.split()
        rgb = Image.merge("RGB", (r, g, b))

        # Adjust brightness
        enhancer = ImageEnhance.Brightness(rgb)
        brightness_factor = 0.7 + (bg_brightness * 0.6)  # Range: 0.7-1.3
        rgb = enhancer.enhance(brightness_factor)

        # Slight color temperature adjustment
        if bg_mean[0] > bg_mean[2]:  # Warm background
            rgb = self._adjust_temperature(rgb, warmth=0.05)
        else:  # Cool background
            rgb = self._adjust_temperature(rgb, warmth=-0.05)

        # Merge back with alpha
        r, g, b = rgb.split()
        return Image.merge("RGBA", (r, g, b, a))

    def _adjust_temperature(
        self,
        image: Image.Image,
        warmth: float,
    ) -> Image.Image:
        """Adjust color temperature of an image."""
        r, g, b = image.split()

        r = r.point(lambda x: min(255, int(x * (1 + warmth))))
        b = b.point(lambda x: max(0, int(x * (1 - warmth))))

        return Image.merge("RGB", (r, g, b))


# Singleton instance
compositor = Compositor()
