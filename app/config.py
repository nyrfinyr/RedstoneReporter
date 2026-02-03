"""Configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "redstone_reporter"

    # Storage
    SCREENSHOT_DIR: Path = Path("./data/screenshots")

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Limits
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_SCREENSHOT_DIMENSION: int = 4096     # pixels

    # UI
    RUNS_PER_PAGE: int = 50
    AUTO_REFRESH_INTERVAL: int = 5  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()

# Auto-create required directories
settings.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
