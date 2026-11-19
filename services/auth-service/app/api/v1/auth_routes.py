from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserCreate, UserLogin, Token, UserResponse
from app.core.security import decode_access_token
from uuid import UUID

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new customer account."""
    try:
        auth_service = AuthService(db)
        return await auth_service.register_customer(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate a user and return a JWT token."""
    try:
        auth_service = AuthService(db)
        return await auth_service.login(user_data.email, user_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the current user profile."""
    try:
        auth_service = AuthService(db)
        return await auth_service.get_current_user(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token deletion)."""
    return {"message": "Successfully logged out"}
