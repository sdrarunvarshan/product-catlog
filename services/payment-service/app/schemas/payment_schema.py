from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.payment import PaymentStatus


class PaymentBase(BaseModel):
    """Base payment schema."""
    order_id: UUID
    customer_id: UUID
    amount: Decimal


class PaymentResponse(PaymentBase):
    """Schema for payment response."""
    id: UUID
    payment_status: PaymentStatus
    transaction_reference: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentStatusResponse(BaseModel):
    """Schema for payment status check."""
    payment_id: UUID
    order_id: UUID
    payment_status: PaymentStatus
    transaction_reference: str
