from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service
    SERVICE_NAME: str = "product-service"
    SERVICE_PORT: int = 8002

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ecommerce_products"

    # Auth Service (for role verification)
    AUTH_SERVICE_URL: str = "http://auth-service:8001"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
