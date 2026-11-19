from uuid import UUID
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment, PaymentStatus
from decimal import Decimal
import secrets


class PaymentRepository:
    """Repository for payment database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(
        self,
        order_id: UUID,
        customer_id: UUID,
        amount: Decimal,
        payment_status: PaymentStatus
    ) -> Payment:
        """Create a new payment record."""
        payment = Payment(
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            payment_status=payment_status,
            transaction_reference=self._generate_transaction_reference()
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_payment_by_id(self, payment_id: UUID) -> Optional[Payment]:
        """Get a payment by ID."""
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_payment_by_order_id(self, order_id: UUID) -> Optional[Payment]:
        """Get a payment by order ID."""
        result = await self.db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_payment_by_transaction_reference(
        self,
        reference: str
    ) -> Optional[Payment]:
        """Get a payment by transaction reference."""
        result = await self.db.execute(
            select(Payment).where(Payment.transaction_reference == reference)
        )
        return result.scalar_one_or_none()

    async def payment_exists_for_order(self, order_id: UUID) -> bool:
        """Check if a payment already exists for an order (idempotency)."""
        result = await self.db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none() is not None

    def _generate_transaction_reference(self) -> str:
        """Generate a unique transaction reference."""
        return f"TXN-{secrets.token_urlsafe(16).upper()}"
