import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.base import Base

settings = get_settings()

# Create async engine
engine = create_async_engine(settings.DATABASE_URL.replace("+asyncpg", ""), echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def seed_admin():
    """Create admin user if it doesn't exist."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == settings.ADMIN_EMAIL)
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print(f"Admin user already exists: {settings.ADMIN_EMAIL}")
            return

        # Create admin user
        admin = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            full_name="System Administrator",
            role="ADMIN",
            is_active=True
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print(f"Admin user created successfully: {settings.ADMIN_EMAIL}")
        print(f"Password: {settings.ADMIN_PASSWORD}")


async def main():
    """Main seed function."""
    print("Starting auth service seed...")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed admin
    await seed_admin()

    print("Auth service seed completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
