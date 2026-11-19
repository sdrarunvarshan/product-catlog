from uuid import UUID
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product


class ProductRepository:
    """Repository for product database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(
        self,
        name: str,
        description: Optional[str],
        price: float,
        stock_quantity: int
    ) -> Product:
        """Create a new product."""
        product = Product(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity
        )
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_product_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get a product by ID."""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Product]:
        """List products with pagination."""
        query = select(Product)
        if active_only:
            query = query.where(Product.is_active == True)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_products(self, active_only: bool = True) -> int:
        """Count total products."""
        from sqlalchemy import func
        query = select(func.count(Product.id))
        if active_only:
            query = query.where(Product.is_active == True)
        result = await self.db.execute(query)
        return result.scalar()

    async def update_product(
        self,
        product_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        stock_quantity: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Product]:
        """Update a product."""
        product = await self.get_product_by_id(product_id)
        if not product:
            return None

        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if stock_quantity is not None:
            product.stock_quantity = stock_quantity
        if is_active is not None:
            product.is_active = is_active

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: UUID) -> bool:
        """Delete a product (soft delete by setting is_active=False)."""
        product = await self.get_product_by_id(product_id)
        if not product:
            return False

        product.is_active = False
        await self.db.commit()
        return True

    async def update_stock(self, product_id: UUID, quantity_change: int) -> Optional[Product]:
        """Update product stock quantity."""
        product = await self.get_product_by_id(product_id)
        if not product:
            return None

        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError("Insufficient stock")

        product.stock_quantity = new_quantity
        await self.db.commit()
        await self.db.refresh(product)
        return product
