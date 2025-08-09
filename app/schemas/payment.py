"""Pydantic schemas for Payment and webhook payload."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    """Base payment fields."""

    transaction_id: str
    user_id: int
    account_id: int
    amount: Decimal = Field(gt=0)


class PaymentPublic(PaymentBase):
    """Public representation of a payment."""

    id: int

    class Config:
        from_attributes = True


class WebhookPayment(BaseModel):
    """Webhook payload for top-up processing."""

    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal = Field(gt=0)
    signature: str
