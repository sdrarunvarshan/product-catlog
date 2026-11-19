from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.payment_service import PaymentService
from app.schemas.payment_schema import PaymentStatusResponse, PaymentResponse
from uuid import UUID

router = APIRouter()


@router.get("/{payment_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get the status of a payment."""
    payment_service = PaymentService(db)
    try:
        return await payment_service.get_payment_status(payment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get payment by order ID."""
    payment_service = PaymentService(db)
    payment = await payment_service.get_payment_by_order(order_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment
