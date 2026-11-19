import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import get_settings
from app.models.base import Base
from app.models.payment import Payment

settings = get_settings()

# Create async engine
engine = create_async_engine(settings.DATABASE_URL.replace("+asyncpg", ""), echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def main():
    """Main seed function - just create tables."""
    print("Starting payment service seed...")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Payment service seed completed successfully. Tables created.")


if __name__ == "__main__":
    asyncio.run(main())
