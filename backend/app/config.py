"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Application
    app_name: str = "MockupAI"
    app_env: str = "development"
    debug: bool = True

    # URLs
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # Database (SQLite for MVP simplicity)
    database_url: str = "sqlite+aiosqlite:///./mockupai.db"

    # Gemini API
    gemini_api_key: str = ""

    # Local storage (MVP - no S3 needed)
    upload_dir: Path = Path("uploads")
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        (self.upload_dir / "products").mkdir(exist_ok=True)
        (self.upload_dir / "mockups").mkdir(exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
