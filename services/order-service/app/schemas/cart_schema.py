from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class CartItemBase(BaseModel):
    """Base cart item schema."""
    product_id: UUID
    product_name: str
    quantity: int = Field(..., gt=0)
    unit_price: Decimal
    subtotal: Decimal


class CartItemCreate(BaseModel):
    """Schema for adding item to cart."""
    product_id: UUID
    quantity: int = Field(..., gt=0)


class CartItemResponse(CartItemBase):
    """Schema for cart item response."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Schema for cart response."""
    id: UUID
    customer_id: UUID
    items: list[CartItemResponse]
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
