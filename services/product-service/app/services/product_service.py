from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse


class ProductService:
    """Service for product business logic."""

    def __init__(self, db: AsyncSession):
        self.product_repo = ProductRepository(db)

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create a new product."""
        product = await self.product_repo.create_product(
            name=product_data.name,
            description=product_data.description,
            price=float(product_data.price),
            stock_quantity=product_data.stock_quantity
        )
        return ProductResponse.model_validate(product)

    async def get_product(self, product_id: UUID) -> Optional[ProductResponse]:
        """Get a product by ID."""
        product = await self.product_repo.get_product_by_id(product_id)
        if not product:
            return None
        return ProductResponse.model_validate(product)

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        active_only: bool = True
    ) -> ProductListResponse:
        """List products with pagination."""
        skip = (page - 1) * page_size
        products = await self.product_repo.list_products(skip, page_size, active_only)
        total = await self.product_repo.count_products(active_only)

        return ProductListResponse(
            products=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            page_size=page_size
        )

    async def update_product(
        self,
        product_id: UUID,
        product_data: ProductUpdate
    ) -> Optional[ProductResponse]:
        """Update a product."""
        product = await self.product_repo.update_product(
            product_id=product_id,
            name=product_data.name,
            description=product_data.description,
            price=float(product_data.price) if product_data.price is not None else None,
            stock_quantity=product_data.stock_quantity,
            is_active=None  # Not exposed in update
        )
        if not product:
            return None
        return ProductResponse.model_validate(product)

    async def delete_product(self, product_id: UUID) -> bool:
        """Delete a product (soft delete)."""
        return await self.product_repo.delete_product(product_id)

    async def check_stock(self, product_id: UUID, quantity: int) -> bool:
        """Check if sufficient stock is available."""
        product = await self.product_repo.get_product_by_id(product_id)
        if not product:
            return False
        return product.stock_quantity >= quantity

    async def reduce_stock(self, product_id: UUID, quantity: int) -> bool:
        """Reduce stock after order placement."""
        try:
            await self.product_repo.update_stock(product_id, -quantity)
            return True
        except ValueError:
            return False
