"""Re-export Base from database for backwards compatibility."""
from app.core.database import Base

__all__ = ["Base"]
