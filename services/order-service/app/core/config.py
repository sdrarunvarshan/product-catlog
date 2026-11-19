from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service
    SERVICE_NAME: str = "order-service"
    SERVICE_PORT: int = 8003

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ecommerce_orders"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_ORDER_CREATED_TOPIC: str = "order.created"
    KAFKA_PAYMENT_COMPLETED_TOPIC: str = "payment.completed"
    KAFKA_PAYMENT_FAILED_TOPIC: str = "payment.failed"

    # Product Service
    PRODUCT_SERVICE_URL: str = "http://product-service:8002"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
