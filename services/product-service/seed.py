import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import get_settings
from app.models.product import Product
from app.models.base import Base

settings = get_settings()

# Create async engine
engine = create_async_engine(settings.DATABASE_URL.replace("+asyncpg", ""), echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def seed_products():
    """Create sample products."""
    sample_products = [
        {
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
            "price": 149.99,
            "stock_quantity": 50
        },
        {
            "name": "Smart Watch Series 5",
            "description": "Fitness tracking, heart rate monitor, GPS, and water-resistant smartwatch.",
            "price": 299.99,
            "stock_quantity": 30
        },
        {
            "name": "Portable Power Bank 20000mAh",
            "description": "Fast charging power bank with USB-C and multiple USB ports.",
            "price": 49.99,
            "stock_quantity": 100
        },
        {
            "name": "USB-C Hub Adapter",
            "description": "7-in-1 USB-C hub with HDMI, USB 3.0, SD card reader, and PD charging.",
            "price": 39.99,
            "stock_quantity": 75
        },
        {
            "name": "Mechanical Gaming Keyboard",
            "description": "RGB backlit mechanical keyboard with blue switches and programmable keys.",
            "price": 89.99,
            "stock_quantity": 40
        }
    ]

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        # Check if products already exist
        result = await session.execute(select(Product))
        existing_count = len(result.scalars().all())

        if existing_count > 0:
            print(f"Products already exist ({existing_count} products). Skipping seed.")
            return

        # Create products
        for product_data in sample_products:
            product = Product(**product_data)
            session.add(product)

        await session.commit()
        print(f"Created {len(sample_products)} sample products.")


async def main():
    """Main seed function."""
    print("Starting product service seed...")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed products
    await seed_products()

    print("Product service seed completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
