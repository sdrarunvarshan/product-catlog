from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service
    SERVICE_NAME: str = "payment-service"
    SERVICE_PORT: int = 8004

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ecommerce_payments"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_ORDER_CREATED_TOPIC: str = "order.created"
    KAFKA_PAYMENT_COMPLETED_TOPIC: str = "payment.completed"
    KAFKA_PAYMENT_FAILED_TOPIC: str = "payment.failed"

    # Payment settings
    MOCK_PAYMENT_SUCCESS_RATE: float = 0.8  # 80% success rate for mock payments

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
