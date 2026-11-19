from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.schemas.order_schema import OrderResponse, OrderStatusUpdate
from app.models.order import OrderStatus
from decimal import Decimal


class OrderService:
    """Service for order business logic."""

    def __init__(self, db: AsyncSession):
        self.order_repo = OrderRepository(db)
        self.cart_repo = CartRepository(db)

    async def create_order_from_cart(self, customer_id: UUID) -> OrderResponse:
        """Create an order from the customer's cart."""
        # Get cart
        cart = await self.cart_repo.get_cart(customer_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty")

        # Calculate total
        total_amount = await self.cart_repo.get_cart_total(cart.id)

        # Prepare order items data
        items_data = [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal
            }
            for item in cart.items
        ]

        # Create order
        order = await self.order_repo.create_order(customer_id, total_amount, items_data)

        # Clear cart
        await self.cart_repo.clear_cart(cart.id)

        return OrderResponse.model_validate(order)

    async def get_order(self, order_id: UUID) -> OrderResponse:
        """Get an order by ID."""
        order = await self.order_repo.get_order(order_id)
        if not order:
            raise ValueError("Order not found")
        return OrderResponse.model_validate(order)

    async def get_customer_orders(
        self,
        customer_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> List[OrderResponse]:
        """Get all orders for a customer."""
        skip = (page - 1) * page_size
        orders = await self.order_repo.get_customer_orders(customer_id, skip, page_size)
        return [OrderResponse.model_validate(order) for order in orders]

    async def get_all_orders(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> List[OrderResponse]:
        """Get all orders (admin)."""
        skip = (page - 1) * page_size
        orders = await self.order_repo.get_all_orders(skip, page_size)
        return [OrderResponse.model_validate(order) for order in orders]

    async def update_order_status(
        self,
        order_id: UUID,
        status_update: OrderStatusUpdate
    ) -> OrderResponse:
        """Update the status of an order."""
        order = await self.order_repo.update_order_status(order_id, status_update.status)
        if not order:
            raise ValueError("Order not found")
        return OrderResponse.model_validate(order)
