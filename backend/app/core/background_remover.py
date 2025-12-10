"""Background removal service using rembg."""
from PIL import Image
from rembg import remove
import io
import logging

logger = logging.getLogger(__name__)


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

        # Remove background
        output_bytes = remove(img_bytes)

        # Convert back to PIL Image
        return Image.open(io.BytesIO(output_bytes))

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
