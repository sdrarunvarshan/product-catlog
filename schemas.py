from pydantic import BaseModel

# Base schema - shared fields between create/update/read
class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    quantity: int

# Schema for creating a new product (no ID yet)
class ProductCreate(ProductBase):
    pass

# Schema for updating a product (same fields)
class ProductUpdate(ProductBase):
    pass

# Schema for reading a product (includes ID)
class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True  # Allows reading data directly from ORM models
