from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.events.producer import kafka_producer
from app.events.consumer import KafkaEventConsumer
from app.db.session import AsyncSessionLocal

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    await kafka_producer.start()

    # Start Kafka consumer
    consumer = KafkaEventConsumer(AsyncSessionLocal)
    await consumer.start()

    yield

    # Shutdown
    await kafka_producer.stop()
    await consumer.stop()


app = FastAPI(
    title="Order Service",
    description="Order microservice for e-commerce platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
