"""Background removal service using rembg with post-processing refinements."""
from PIL import Image, ImageFilter, ImageOps
from rembg import remove
import io
import logging
import numpy as np

logger = logging.getLogger(__name__)


def _refine_alpha(matte: Image.Image, original: Image.Image) -> Image.Image:
    """Feather edges, rescue glass/reflective areas, and keep soft shadows."""
    if matte.mode != "RGBA":
        matte = matte.convert("RGBA")
    if original.mode != "RGBA":
        original = original.convert("RGBA")

    r, g, b, alpha = matte.split()
    alpha_np = np.array(alpha).astype(np.float32)

    # Feather edges to avoid harsh cutouts
    feathered = Image.fromarray(alpha_np).filter(ImageFilter.GaussianBlur(radius=1.5))
    alpha_np = np.array(feathered).astype(np.float32)

    # Recover highlights on transparent/glass products by lifting alpha where
    # the product is bright but got cut too aggressively.
    original_np = np.array(original.convert("RGB")).astype(np.float32)
    brightness = original_np.mean(axis=2)
    glass_mask = (brightness > 200) & (alpha_np < 120)
    alpha_np = np.where(glass_mask, alpha_np * 0.4 + 80, alpha_np)

    # Re-introduce soft contact shadows near the product footprint
    alpha_img = Image.fromarray(alpha_np.astype(np.uint8))
    dilated = alpha_img.filter(ImageFilter.MaxFilter(size=5))
    dilated_np = np.array(dilated).astype(np.float32) / 255.0
    gray = ImageOps.grayscale(original)
    gray_np = np.array(gray).astype(np.float32) / 255.0
    shadow_candidates = (1.0 - dilated_np) * (0.6 - gray_np)
    shadow_mask = np.clip(shadow_candidates * 255 * 0.5, 0, 50)
    alpha_np = np.clip(alpha_np + shadow_mask, 0, 255)

    refined_alpha = Image.fromarray(alpha_np.astype(np.uint8))
    return Image.merge("RGBA", (r, g, b, refined_alpha))


async def remove_background(image: Image.Image) -> Image.Image:
    """
    Remove background from a product image.

    Args:
        image: PIL Image with product

    Returns:
        PIL Image with transparent background
    """
    try:
        # Convert to bytes for rembg
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()

        # Remove background with alpha matting to keep fine details
        output_bytes = remove(
            img_bytes,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10,
        )

        # Convert back to PIL Image and refine mask
        matte = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        return _refine_alpha(matte, image)

    except Exception as e:
        logger.error(f"Background removal failed: {e}")
        # Return original image if removal fails
        return image


def get_product_bounds(image: Image.Image) -> tuple:
    """
    Get bounding box of non-transparent pixels.

    Returns:
        (left, top, right, bottom) tuple
    """
    if image.mode != "RGBA":
        return (0, 0, image.width, image.height)

    # Get bounding box of non-transparent area
    bbox = image.getbbox()
    if bbox:
        return bbox
    return (0, 0, image.width, image.height)
