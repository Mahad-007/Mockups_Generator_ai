"""Local file storage for MVP."""
from pathlib import Path
from PIL import Image
import uuid
import io
from datetime import datetime

from app.config import settings


def save_image(image: Image.Image, folder: str, filename: str = None) -> str:
    """
    Save an image to local storage.

    Args:
        image: PIL Image to save
        folder: Subfolder (products, mockups)
        filename: Optional filename, auto-generated if not provided

    Returns:
        Relative path to saved file
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.png"

    # Ensure folder exists
    folder_path = settings.upload_dir / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    # Save image
    file_path = folder_path / filename
    image.save(file_path, format="PNG")

    return f"{folder}/{filename}"


def save_upload(file_bytes: bytes, folder: str, original_filename: str) -> str:
    """
    Save uploaded file bytes to local storage.

    Args:
        file_bytes: Raw file bytes
        folder: Subfolder (products, mockups)
        original_filename: Original filename for extension

    Returns:
        Relative path to saved file
    """
    ext = Path(original_filename).suffix or ".png"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uuid.uuid4().hex[:8]}{ext}"

    folder_path = settings.upload_dir / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    file_path = folder_path / filename
    file_path.write_bytes(file_bytes)

    return f"{folder}/{filename}"


def get_image(relative_path: str) -> Image.Image:
    """Load an image from local storage."""
    file_path = settings.upload_dir / relative_path
    return Image.open(file_path)


def get_full_path(relative_path: str) -> Path:
    """Get full path from relative path."""
    return settings.upload_dir / relative_path


def delete_file(relative_path: str) -> bool:
    """Delete a file from storage."""
    try:
        file_path = settings.upload_dir / relative_path
        file_path.unlink(missing_ok=True)
        return True
    except Exception:
        return False
