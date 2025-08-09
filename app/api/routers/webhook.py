"""Webhook route to process external payment notifications."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.schemas.payment import PaymentPublic, WebhookPayment
from app.services.payments import compute_webhook_signature, process_webhook
from app.db.session import get_db_session

router = APIRouter(prefix='/webhook', tags=['webhook'])


@router.post('/payment', response_model=PaymentPublic, summary='Process payment webhook')
async def webhook_payment(payload: WebhookPayment, db: AsyncSession = Depends(get_db_session)) -> PaymentPublic:
    settings = get_settings()
    expected_signature = compute_webhook_signature(
        account_id=payload.account_id,
        amount=payload.amount,
        transaction_id=payload.transaction_id,
        user_id=payload.user_id,
        secret_key=settings.webhook_secret_key,
    )
    if payload.signature != expected_signature:
        raise HTTPException(status_code=400, detail='Invalid signature')

    payment = await process_webhook(
        db,
        transaction_id=payload.transaction_id,
        account_id=payload.account_id,
        user_id=payload.user_id,
        amount=payload.amount,
    )
    return PaymentPublic.model_validate(payment)
