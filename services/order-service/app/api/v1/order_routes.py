from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.services.order_service import OrderService
from app.schemas.order_schema import OrderResponse, OrderStatusUpdate
from app.events.producer import kafka_producer
from uuid import UUID

router = APIRouter()


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def checkout(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Checkout and create an order from the cart."""
    order_service = OrderService(db)
    try:
        order = await order_service.create_order_from_cart(customer_id)

        # Publish order.created event to Kafka
        await kafka_producer.publish_order_created(
            order.id,
            order.customer_id,
            order.total_amount
        )

        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    customer_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List orders. If customer_id is provided, returns only that customer's orders."""
    order_service = OrderService(db)
    if customer_id:
        return await order_service.get_customer_orders(customer_id, page, page_size)
    else:
        # Admin view - all orders
        return await order_service.get_all_orders(page, page_size)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get an order by ID."""
    order_service = OrderService(db)
    try:
        return await order_service.get_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update the status of an order (admin only)."""
    # Note: In production, add role verification middleware here
    order_service = OrderService(db)
    try:
        return await order_service.update_order_status(order_id, status_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
