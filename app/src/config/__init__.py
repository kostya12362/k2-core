from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_PATH = Path(__file__).parent.parent.parent


class APIUrlsSettings(BaseModel):
    """Configure public urls."""

    docs: str = "/docs"
    redoc: str = "/redoc"
    prefix: str = "/api/v1"


class CorsSettings(BaseModel):
    allow_origins: list[str] = ["*"]


class PublicApiSettings(BaseModel):
    """Configure public API settings."""

    name: str = "Products API"
    urls: APIUrlsSettings = APIUrlsSettings()
    cors: CorsSettings = CorsSettings()


class ServiceSettings(BaseModel):
    """Identification and environment stage settings for the service."""

    namespace: str = "auctions-data-collector"
    name: str = "data-collector"
    version: str
    stage: str
    instance: str | None = None


class LoggerSettings(BaseModel):
    """Logging configuration including verbosity and output path."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    path: Path | None = None


class BaseUriSettings(BaseModel):
    uri: str


class BrokerSettings(BaseUriSettings):
    """Message broker connection settings."""


class RedisSettings(BaseUriSettings):
    """Configuration for Redis connection used for caching and state."""


class DatabaseSettings(BaseUriSettings):
    """Configuration for database connection."""

    pool_size: int = 30
    max_overflow: int = 15
    pool_timeout: int = 120
    pool_recycle: int = 900


class Settings(BaseSettings):
    debug: bool = True
    public_api: PublicApiSettings = PublicApiSettings()
    service: ServiceSettings
    logger: LoggerSettings = LoggerSettings()
    database: DatabaseSettings

    model_config = SettingsConfigDict(
        env_file=ROOT_PATH / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
    )


settings = Settings()
