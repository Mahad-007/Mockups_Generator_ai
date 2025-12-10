"""Shared utility functions."""
from app.config import settings


def get_image_url(path: str) -> str:
    """Convert a storage path to a full URL."""
    return f"{settings.backend_url}/uploads/{path}"
