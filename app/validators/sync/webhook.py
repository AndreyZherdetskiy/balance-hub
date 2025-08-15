from __future__ import annotations

from app.core.constants import DomainConstraints, ErrorMessages, MonetaryConstants
from app.core.errors import ValidationError
from app.schemas import WebhookPayment
from app.utils.crypto import compute_signature


class WebhookValidator:
    """Валидатор вебхуков платежей."""

    @staticmethod
    def validate_signature(payload: WebhookPayment, *, secret_key: str) -> None:
        """Проверяет подпись вебхука.

        Args:
            payload (WebhookPayment): Данные вебхука.

        Raises:
            ValidationError: Если подпись некорректна.
        """
        expected_signature = compute_signature(
            account_id=payload.account_id,
            amount=payload.amount,
            transaction_id=payload.transaction_id,
            user_id=payload.user_id,
            secret_key=secret_key,
        )
        if payload.signature != expected_signature:
            raise ValidationError(ErrorMessages.INVALID_SIGNATURE)

    @staticmethod
    def validate_payment_data(payload: WebhookPayment) -> None:
        """Проверяет корректность данных платежа.

        Args:
            payload (WebhookPayment): Данные вебхука.

        Raises:
            ValidationError: Если данные некорректны.
        """
        if payload.amount <= MonetaryConstants.ZERO:
            raise ValidationError(ErrorMessages.AMOUNT_MUST_BE_POSITIVE)

        if (
            payload.user_id < DomainConstraints.MIN_ID
            or payload.account_id < DomainConstraints.NO_ACCOUNT
        ):
            raise ValidationError(ErrorMessages.INVALID_USER_OR_ACCOUNT_ID)

        if not payload.transaction_id or not payload.transaction_id.strip():
            raise ValidationError(ErrorMessages.INVALID_TRANSACTION_ID)
