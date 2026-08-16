"""Application configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Values come from .env or the environment."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8",
        extra='ignore'
    )

    # Business rules
    review_threshold_percent: float = Field(default=10.0, gt=0)
    outlier_threshold_percent: float = Field(default=50.0, gt=0)

    #HTTP client
    request_timeout_seconds: int = Field(default=10, gt=0)
    max_attempts: int = Field(default=3, ge=1)
    backoff_base_seconds: float = Field(default=1.0, gt=0)

settings = Settings()