from uuid import UUID
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem, OrderStatus
from decimal import Decimal


class OrderRepository:
    """Repository for order database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        customer_id: UUID,
        total_amount: Decimal,
        items_data: List[dict]
    ) -> Order:
        """Create a new order with items."""
        order = Order(
            customer_id=customer_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING_PAYMENT
        )
        self.db.add(order)
        await self.db.flush()  # Get the order ID without committing

        # Create order items
        for item_data in items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"]
            )
            self.db.add(order_item)

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_order(self, order_id: UUID) -> Optional[Order]:
        """Get an order by ID."""
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_customer_orders(
        self,
        customer_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get all orders for a customer."""
        result = await self.db.execute(
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_orders(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get all orders (admin)."""
        result = await self.db.execute(
            select(Order)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_order_status(
        self,
        order_id: UUID,
        status: OrderStatus
    ) -> Optional[Order]:
        """Update the status of an order."""
        order = await self.get_order(order_id)
        if not order:
            return None

        order.status = status
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def count_orders(self, customer_id: Optional[UUID] = None) -> int:
        """Count orders."""
        from sqlalchemy import func
        query = select(func.count(Order.id))
        if customer_id:
            query = query.where(Order.customer_id == customer_id)
        result = await self.db.execute(query)
        return result.scalar()
