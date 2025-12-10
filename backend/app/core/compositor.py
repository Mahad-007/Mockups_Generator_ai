from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
from typing import Optional, Tuple, Dict


class Compositor:
    """Handles compositing products onto scene backgrounds."""

    async def smart_composite(
        self,
        product: Image.Image,
        background: Image.Image,
        position: Tuple[int, int] = None,
        scale: float = None,
        lighting_hint: Optional[str] = None,
        angle_hint: Optional[str] = None,
        add_reflection: bool = True,
        add_depth_of_field: bool = True,
    ) -> Image.Image:
        """
        Composite with lighting/perspective analysis and quality polish.

        - Estimates lighting direction to orient shadows
        - Matches product color/brightness to scene
        - Adds reflections when surface likely supports it
        - Applies subtle depth-of-field and sharpening
        """
        product = product.convert("RGBA")
        background = background.convert("RGBA")

        bg_stats = self._analyze_background(background)

        # Determine scale and resize product
        if scale is None:
            scale = self._calculate_auto_scale(
                product,
                background,
                max_coverage=bg_stats["coverage_hint"],
            )
        product = product.resize(
            (int(product.width * scale), int(product.height * scale)),
            Image.Resampling.LANCZOS,
        )

        # Light/temperature match
        product = await self.match_lighting(product, background)

        # Perspective alignment based on angle hints
        if angle_hint:
            product = self._apply_perspective_hint(product, angle_hint)

        # Auto position toward lower third if none provided
        if position is None:
            position = self._anchor_position(background.size, product.size)

        # Prepare result and optional depth of field
        base_bg = background.copy()
        if add_depth_of_field:
            base_bg = self._apply_depth_of_field(base_bg, position, product.size)

        # Shadow parameters derived from lighting analysis
        shadow_offset, shadow_blur, shadow_opacity = self._shadow_from_lighting(
            bg_stats,
            lighting_hint,
            product.size,
        )

        result = base_bg

        # Add shadow
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

        # Optional reflection for glossy/flat surfaces
        if add_reflection and bg_stats["supports_reflection"]:
            reflection = await self.add_reflection(
                product,
                background,
                reflection_opacity=bg_stats["reflection_strength"],
                reflection_height=0.28,
            )
            ref_pos = (
                position[0],
                position[1] + product.height - int(product.height * 0.05),
            )
            result.paste(reflection, ref_pos, reflection)

        # Final polish (upscale + light sharpening + grain matching)
        result = self._final_polish(result, bg_stats)
        return result

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

    def _analyze_background(self, background: Image.Image) -> Dict:
        """Lightweight background analysis for lighting/reflection hints."""
        rgb = np.array(background.convert("RGB")).astype(np.float32)
        h, w, _ = rgb.shape

        brightness_map = rgb.mean(axis=2)
        mean_brightness = float(brightness_map.mean() / 255)
        contrast = float(brightness_map.std() / 255)

        # Brightness distribution to infer light direction
        x_weights = np.linspace(-1, 1, w)
        y_weights = np.linspace(-1, 1, h)
        dx = float((brightness_map.mean(axis=0) * x_weights).mean())
        dy = float((brightness_map.mean(axis=1) * y_weights).mean())

        # Surface/reflection heuristic: brighter lower band + low contrast implies glossy
        lower_band = brightness_map[int(h * 0.65) :, :]
        lower_mean = float(lower_band.mean() / 255) if lower_band.size else mean_brightness
        supports_reflection = lower_mean > 0.55 and contrast < 0.18
        reflection_strength = 0.35 if supports_reflection else 0.0

        coverage_hint = 0.55 if contrast > 0.18 else 0.65

        return {
            "brightness": mean_brightness,
            "contrast": contrast,
            "light_direction": (dx, dy),
            "supports_reflection": supports_reflection,
            "reflection_strength": reflection_strength,
            "coverage_hint": coverage_hint,
        }

    def _anchor_position(self, bg_size: Tuple[int, int], product_size: Tuple[int, int]) -> Tuple[int, int]:
        """Place product slightly below center to sit on surface."""
        bw, bh = bg_size
        pw, ph = product_size
        x = (bw - pw) // 2
        y = int(bh * 0.58) - (ph // 2)
        y = max(0, min(y, bh - ph))
        return (x, y)

    def _shadow_from_lighting(
        self,
        bg_stats: Dict,
        lighting_hint: Optional[str],
        product_size: Tuple[int, int],
    ) -> Tuple[Tuple[int, int], int, float]:
        """Derive shadow offset/blur/opacity from lighting cues."""
        dx, dy = bg_stats["light_direction"]
        width, height = product_size
        base_offset = (8, max(8, int(height * 0.04)))

        if lighting_hint:
            hint = lighting_hint.lower()
            if "left" in hint:
                dx = -0.8
            elif "right" in hint:
                dx = 0.8
            if "top" in hint:
                dy = -0.4
            elif "bottom" in hint:
                dy = 0.6

        offset = (
            int(base_offset[0] + dx * 12),
            int(base_offset[1] + dy * 10),
        )
        blur = max(10, int(min(width, height) * (0.06 + bg_stats["contrast"] * 0.3)))
        opacity = 0.22 + min(bg_stats["contrast"] * 0.9, 0.35)
        return offset, blur, opacity

    def _apply_perspective_hint(self, image: Image.Image, hint: str) -> Image.Image:
        """Apply a mild perspective warp based on angle hint."""
        hint = hint.lower()
        shear_x = 0.0
        shear_y = 0.0

        if "top" in hint:
            shear_y = -0.08
        elif "low" in hint or "side" in hint:
            shear_y = 0.05

        if "45" in hint or "angle" in hint:
            shear_x = 0.08
        elif "side" in hint:
            shear_x = 0.12

        if shear_x == 0 and shear_y == 0:
            return image

        w, h = image.size
        matrix = (1, shear_x, 0, shear_y, 1, 0)
        return image.transform(
            (w, h),
            Image.Transform.AFFINE,
            matrix,
            resample=Image.Resampling.BICUBIC,
            fillcolor=(0, 0, 0, 0),
        )

    def _apply_depth_of_field(
        self,
        background: Image.Image,
        position: Tuple[int, int],
        product_size: Tuple[int, int],
    ) -> Image.Image:
        """Subtle background blur outside the product focus zone."""
        blurred = background.filter(ImageFilter.GaussianBlur(radius=2.8))
        mask = Image.new("L", background.size, 255)
        draw = ImageDraw.Draw(mask)

        pad_w = int(product_size[0] * 0.35)
        pad_h = int(product_size[1] * 0.35)
        box = (
            max(0, position[0] - pad_w),
            max(0, position[1] - pad_h),
            min(background.width, position[0] + product_size[0] + pad_w),
            min(background.height, position[1] + product_size[1] + pad_h),
        )
        draw.rectangle(box, fill=0)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=12))
        return Image.composite(blurred, background, mask)

    def _final_polish(self, image: Image.Image, bg_stats: Dict) -> Image.Image:
        """Upscale small outputs, add light sharpening and grain to match scene texture."""
        target_min = 1400
        w, h = image.size
        if min(w, h) < target_min:
            scale = target_min / min(w, h)
            image = image.resize(
                (int(w * scale), int(h * scale)),
                Image.Resampling.LANCZOS,
            )
            w, h = image.size

        image = image.filter(ImageFilter.UnsharpMask(radius=1.4, percent=120, threshold=3))

        # Subtle noise to blend product and scene
        noise_strength = 0.012 + (bg_stats["contrast"] * 0.01)
        arr = np.array(image).astype(np.float32)
        noise = np.random.normal(0, 255 * noise_strength, size=arr.shape[:2] + (1,))
        if arr.shape[2] == 4:
            rgb = arr[:, :, :3]
            alpha = arr[:, :, 3:]
            rgb = np.clip(rgb + noise, 0, 255)
            arr = np.concatenate([rgb, alpha], axis=2)
        else:
            arr = np.clip(arr + noise, 0, 255)

        return Image.fromarray(arr.astype(np.uint8))


# Singleton instance
compositor = Compositor()
