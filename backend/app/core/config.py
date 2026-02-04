"""Application configuration management using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Agentex"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/agentex"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_DEFAULT_TTL: int = 3600
    REDIS_SENTINEL_HOSTS: str = Field(default="")
    REDIS_SENTINEL_SERVICE_NAME: str = Field(default="")
    REDIS_SENTINEL_PASSWORD: str | None = None

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT encoding",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = Field(default="*")
    CORS_ALLOW_HEADERS: str = Field(default="*")

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "console"

    # Vector Database (Milvus)
    VECTOR_DB_TYPE: Literal["milvus", "qdrant"] = "milvus"
    VECTOR_DB_HOST: str = "localhost"
    VECTOR_DB_PORT: int = 19530

    # File Storage
    STORAGE_TYPE: Literal["local", "minio"] = "local"
    STORAGE_PATH: str = "./storage"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]

    @property
    def cors_allow_methods_list(self) -> list[str]:
        """Parse CORS methods."""
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        return [
            method.strip()
            for method in self.CORS_ALLOW_METHODS.split(",")
            if method.strip()
        ]

    @property
    def cors_allow_headers_list(self) -> list[str]:
        """Parse CORS headers."""
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        return [
            header.strip()
            for header in self.CORS_ALLOW_HEADERS.split(",")
            if header.strip()
        ]

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return str(self.DATABASE_URL).replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
