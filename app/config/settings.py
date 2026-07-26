"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "PDF Extractext"
    debug: bool = False
    max_file_size: int = 10 * 1024 * 1024
    mongodb_uri: str = "mongodb://root:qwerty1234@localhost:27017?authSource=admin"
    mongodb_database: str = "pdf_extractext"
    model_config = SettingsConfigDict(env_file=".env", extra = "ignore")



settings = Settings()
