from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment_schema import PaymentResponse, PaymentStatusResponse
from app.models.payment import PaymentStatus
from app.core.config import get_settings
from decimal import Decimal
import random

settings = get_settings()


class PaymentService:
    """Service for payment business logic."""

    def __init__(self, db: AsyncSession):
        self.payment_repo = PaymentRepository(db)

    async def process_payment(
        self,
        order_id: UUID,
        customer_id: UUID,
        amount: Decimal
    ) -> PaymentResponse:
        """Process a mock payment for an order."""
        # Check for idempotency - payment already processed
        if await self.payment_repo.payment_exists_for_order(order_id):
            existing_payment = await self.payment_repo.get_payment_by_order_id(order_id)
            return PaymentResponse.model_validate(existing_payment)

        # Simulate payment processing with random success/failure
        success = random.random() < settings.MOCK_PAYMENT_SUCCESS_RATE

        payment_status = PaymentStatus.SUCCESS if success else PaymentStatus.FAILED

        # Create payment record
        payment = await self.payment_repo.create_payment(
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            payment_status=payment_status
        )

        return PaymentResponse.model_validate(payment)

    async def get_payment_status(self, payment_id: UUID) -> PaymentStatusResponse:
        """Get the status of a payment."""
        payment = await self.payment_repo.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")

        return PaymentStatusResponse(
            payment_id=payment.id,
            order_id=payment.order_id,
            payment_status=payment.payment_status,
            transaction_reference=payment.transaction_reference
        )

    async def get_payment_by_order(self, order_id: UUID) -> Optional[PaymentResponse]:
        """Get payment by order ID."""
        payment = await self.payment_repo.get_payment_by_order_id(order_id)
        if not payment:
            return None
        return PaymentResponse.model_validate(payment)
