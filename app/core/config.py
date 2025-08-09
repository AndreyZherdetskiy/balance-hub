"""Application configuration using pydantic-settings."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'BalanceHub'
    env: str = 'dev'
    debug: bool = True

    cors_origins: List[AnyHttpUrl] | List[str] = ['*']

    rate_limit: str = '100/minute'

    jwt_secret: str
    jwt_algorithm: str = 'HS256'
    jwt_expires_minutes: int = 60

    webhook_secret_key: str

    database_url: str
    sync_database_url: str

    @field_validator('cors_origins', mode='before')
    def split_cors_origins(cls, value: str | List[str]):  # type: ignore[override]
        if isinstance(value, str):
            if value == '*':
                return ['*']
            return [v.strip() for v in value.split(',') if v.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()  # type: ignore[call-arg]
