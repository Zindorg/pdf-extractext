"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "PDF Extractext"
    debug: bool = False
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # MongoDB Configuration (user provides these)
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "pdf_extractext"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
