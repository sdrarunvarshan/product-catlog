from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(..., ge=0)


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(ProductBase):
    """Schema for updating a product."""
    pass


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list."""
    products: list[ProductResponse]
    total: int
    page: int
    page_size: int
