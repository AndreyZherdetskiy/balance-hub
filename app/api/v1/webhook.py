"""Маршрут вебхука для обработки платежей пополнения."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import (
    ApiDescription,
    ApiErrorResponses,
    ApiSuccessResponses,
    ApiSummary,
    WebhookPaths,
)
from app.core.deps import get_webhook_service
from app.db.session import get_db_session
from app.schemas import PaymentPublic, WebhookPayment
from app.services import WebhookService
from app.validators import WebhookValidator


router = APIRouter(prefix=WebhookPaths.PREFIX, tags=[WebhookPaths.TAG])


@router.post(
    WebhookPaths.PAYMENT,
    response_model=PaymentPublic,
    summary=ApiSummary.WEBHOOK_PAYMENT,
    description=ApiDescription.WEBHOOK_PAYMENT,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: ApiSuccessResponses.WEBHOOK_PAYMENT_201,
        400: ApiErrorResponses.INVALID_PAYMENT_DATA,
        409: ApiErrorResponses.TRANSACTION_ALREADY_PROCESSED,
    },
)
async def webhook_payment(
    payload: WebhookPayment,
    db: AsyncSession = Depends(get_db_session),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> PaymentPublic:
    """Проверяет подпись и обрабатывает пополнение баланса.

    Args:
        payload (WebhookPayment): Тело вебхука.
        db (AsyncSession): Сессия БД.
        webhook_service (WebhookService): Сервис для работы с вебхуками.

    Returns:
        PaymentPublic: Информация о платеже.

    Raises:
        HTTPException: 400 при некорректных данных платежа или неверной подписи.
        HTTPException: 409 при уже обработанной транзакции.
    """
    WebhookValidator.validate_payment_data(payload)

    settings = get_settings()
    WebhookValidator.validate_signature(payload, secret_key=settings.webhook_secret_key)

    payment = await webhook_service.process_topup(
        db,
        transaction_id=payload.transaction_id,
        account_id=payload.account_id,
        user_id=payload.user_id,
        amount=payload.amount,
    )
    return PaymentPublic.model_validate(payment)
