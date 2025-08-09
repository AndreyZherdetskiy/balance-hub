"""Payments service: listing and webhook processing."""
from __future__ import annotations

import hashlib
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.account import Account
from app.models.payment import Payment


def compute_webhook_signature(account_id: int, amount: Decimal, transaction_id: str, user_id: int, secret_key: str) -> str:
    """Compute SHA256 signature of webhook payload with secret."""
    # Concatenation in alphabetical order of keys + secret: {account_id}{amount}{transaction_id}{user_id}{secret_key}
    payload = f"{account_id}{amount}{transaction_id}{user_id}{secret_key}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


async def list_user_payments(db: AsyncSession, user_id: int) -> list[Payment]:
    """List payments for a given user."""
    result = await db.execute(select(Payment).where(Payment.user_id == user_id))
    return result.scalars().all()


async def process_webhook(db: AsyncSession, *, transaction_id: str, account_id: int, user_id: int, amount: Decimal) -> Payment:
    """Idempotently process a top-up webhook: ensure account exists, create payment, update balance."""
    # Ensure account exists and belongs to user; if not, create new for user
    account: Account | None = None
    if account_id:
        result = await db.execute(select(Account).where(Account.id == account_id, Account.user_id == user_id))
        account = result.scalar_one_or_none()
    if not account:
        account = Account(user_id=user_id)
        db.add(account)
        await db.flush()

    payment = Payment(transaction_id=transaction_id, user_id=user_id, account_id=account.id, amount=amount)
    db.add(payment)
    try:
        # Update balance and commit together for atomicity
        account.balance = (account.balance or Decimal('0.00')) + amount
        await db.commit()
    except IntegrityError:
        # Duplicate transaction_id => idempotent: fetch existing payment
        await db.rollback()
        result = await db.execute(select(Payment).where(Payment.transaction_id == transaction_id))
        existing = result.scalar_one_or_none()
        if existing is None:
            raise
        return existing

    await db.refresh(payment)
    return payment
