"""Pydantic-схемы для платежей и вебхука."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants.field_constraints import FieldConstraints
from app.core.constants.money import MonetaryConstants


class PaymentBase(BaseModel):
    """Базовые поля платежа."""

    transaction_id: str = Field(
        min_length=FieldConstraints.TRANSACTION_ID_MIN_LENGTH,
        max_length=FieldConstraints.TRANSACTION_ID_MAX_LENGTH,
    )
    user_id: int
    account_id: int
    amount: Decimal = Field(gt=MonetaryConstants.ZERO)

    @field_validator('amount')
    @classmethod
    def normalize_amount(cls, v: Decimal) -> Decimal:
        """Нормализует сумму до двух знаков после запятой.

        Args:
            v (Decimal): Входная сумма.

        Returns:
            Decimal: Нормализованная сумма с точностью до копеек.
        """
        return v.quantize(MonetaryConstants.ONE_CENT)


class PaymentPublic(PaymentBase):
    """Публичное представление платежа."""

    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'id': 10,
                    'transaction_id': '5eae174f-7cd0-472c-bd36-35660f00132b',
                    'user_id': 1,
                    'account_id': 1,
                    'amount': '100.00',
                }
            ]
        },
    )


class WebhookPayment(PaymentBase):
    """Тело запроса вебхука пополнения."""

    signature: str

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'transaction_id': '5eae174f-7cd0-472c-bd36-35660f00132b',
                    'user_id': 1,
                    'account_id': 1,
                    'amount': 100,
                    'signature': (
                        '7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8'
                    ),
                }
            ]
        }
    )
