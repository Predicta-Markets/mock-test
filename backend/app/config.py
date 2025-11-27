from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env files."""

    database_url: str = "postgresql+asyncpg://predicta:predicta@localhost:5432/predicta"
    app_env: str = "development"
    log_level: str = "info"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance to avoid re-parsing the environment."""
    return Settings()

