import pytest
import sys
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Add service directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'auth-service'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'product-service'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'order-service'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'payment-service'))


@pytest.fixture
async def auth_client():
    """Fixture for Auth Service test client."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
async def product_client():
    """Fixture for Product Service test client."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
async def order_client():
    """Fixture for Order Service test client."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
async def payment_client():
    """Fixture for Payment Service test client."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_db():
    """Fixture for test database session."""
    # Use a separate test database
    engine = create_async_engine(
        "postgresql+asyncpg://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_auth_test",
        echo=False
    )
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()
