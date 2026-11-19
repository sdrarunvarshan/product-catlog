from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.order import OrderStatus


class OrderItemBase(BaseModel):
    """Base order item schema."""
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderItemResponse(OrderItemBase):
    """Schema for order item response."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order schema."""
    customer_id: UUID
    total_amount: Decimal
    status: OrderStatus


class OrderResponse(OrderBase):
    """Schema for order response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating an order (checkout)."""
    # Order is created from cart, so no input needed
    pass


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus
