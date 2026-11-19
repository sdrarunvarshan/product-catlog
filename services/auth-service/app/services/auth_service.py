from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse, Token, TokenData
from app.core.security import create_access_token, decode_access_token
from app.core.config import get_settings
from datetime import timedelta

settings = get_settings()


class AuthService:
    """Service for authentication business logic."""

    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register_customer(
        self,
        user_data: UserCreate
    ) -> Token:
        """Register a new customer account."""
        # Check if email already exists
        if await self.user_repo.email_exists(user_data.email):
            raise ValueError("Email already registered")

        # Create user with CUSTOMER role
        user = await self.user_repo.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role="CUSTOMER"
        )

        # Generate access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )

        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    async def login(self, email: str, password: str) -> Token:
        """Authenticate a user and return a token."""
        user = await self.user_repo.authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is inactive")

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )

        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    async def get_current_user(self, token: str) -> UserResponse:
        """Get the current user from a JWT token."""
        payload = decode_access_token(token)
        if payload is None:
            raise ValueError("Invalid token")

        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token")

        user = await self.user_repo.get_user_by_id(UUID(user_id))
        if user is None:
            raise ValueError("User not found")

        return UserResponse.model_validate(user)

    async def verify_token(self, token: str) -> TokenData:
        """Verify a token and return the token data."""
        payload = decode_access_token(token)
        if payload is None:
            raise ValueError("Invalid token")

        return TokenData(
            user_id=UUID(payload.get("sub")) if payload.get("sub") else None,
            email=payload.get("email"),
            role=payload.get("role")
        )
