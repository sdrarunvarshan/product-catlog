from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cart_repository import CartRepository
from app.schemas.cart_schema import CartResponse, CartItemCreate, CartItemResponse
from decimal import Decimal
import httpx


class CartService:
    """Service for cart business logic."""

    def __init__(self, db: AsyncSession):
        self.cart_repo = CartRepository(db)

    async def get_cart(self, customer_id: UUID) -> Optional[CartResponse]:
        """Get a customer's cart."""
        cart = await self.cart_repo.get_cart(customer_id)
        if not cart:
            return None

        total_amount = await self.cart_repo.get_cart_total(cart.id)

        return CartResponse(
            id=cart.id,
            customer_id=cart.customer_id,
            items=[CartItemResponse.model_validate(item) for item in cart.items],
            total_amount=total_amount,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

    async def add_to_cart(
        self,
        customer_id: UUID,
        item_data: CartItemCreate,
        product_service_url: str
    ) -> CartResponse:
        """Add an item to the cart."""
        # Get product details from product service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{product_service_url}/api/v1/products/{item_data.product_id}"
            )
            if response.status_code != 200:
                raise ValueError("Product not found")

            product = response.json()
            product_name = product["name"]
            unit_price = Decimal(str(product["price"]))

        # Get or create cart
        cart = await self.cart_repo.get_or_create_cart(customer_id)

        # Add item to cart
        await self.cart_repo.add_item(
            cart_id=cart.id,
            product_id=item_data.product_id,
            product_name=product_name,
            quantity=item_data.quantity,
            unit_price=unit_price
        )

        # Return updated cart
        return await self.get_cart(customer_id)

    async def update_cart_item(
        self,
        customer_id: UUID,
        product_id: UUID,
        quantity: int
    ) -> Optional[CartResponse]:
        """Update the quantity of a cart item."""
        cart = await self.cart_repo.get_cart(customer_id)
        if not cart:
            return None

        await self.cart_repo.update_item_quantity(cart.id, product_id, quantity)
        return await self.get_cart(customer_id)

    async def remove_from_cart(
        self,
        customer_id: UUID,
        product_id: UUID
    ) -> Optional[CartResponse]:
        """Remove an item from the cart."""
        cart = await self.cart_repo.get_cart(customer_id)
        if not cart:
            return None

        await self.cart_repo.remove_item(cart.id, product_id)
        return await self.get_cart(customer_id)

    async def clear_cart(self, customer_id: UUID) -> bool:
        """Clear all items from the cart."""
        cart = await self.cart_repo.get_cart(customer_id)
        if not cart:
            return False

        await self.cart_repo.clear_cart(cart.id)
        return True
