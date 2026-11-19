from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.cart_service import CartService
from app.schemas.cart_schema import CartItemCreate, CartResponse
from uuid import UUID
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/", response_model=CartResponse)
async def get_cart(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a customer's shopping cart."""
    cart_service = CartService(db)
    cart = await cart_service.get_cart(customer_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart


@router.post("/items", response_model=CartResponse)
async def add_to_cart(
    customer_id: UUID,
    item_data: CartItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add an item to the shopping cart."""
    cart_service = CartService(db)
    try:
        return await cart_service.add_to_cart(
            customer_id,
            item_data,
            settings.PRODUCT_SERVICE_URL
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/items/{product_id}", response_model=CartResponse)
async def update_cart_item(
    customer_id: UUID,
    product_id: UUID,
    quantity: int,
    db: AsyncSession = Depends(get_db)
):
    """Update the quantity of a cart item."""
    cart_service = CartService(db)
    cart = await cart_service.update_cart_item(customer_id, product_id, quantity)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart


@router.delete("/items/{product_id}", response_model=CartResponse)
async def remove_from_cart(
    customer_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Remove an item from the shopping cart."""
    cart_service = CartService(db)
    cart = await cart_service.remove_from_cart(customer_id, product_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Clear all items from the shopping cart."""
    cart_service = CartService(db)
    success = await cart_service.clear_cart(customer_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
