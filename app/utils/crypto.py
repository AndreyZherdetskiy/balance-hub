"""Криптографические утилиты.

Содержит чистые функции без зависимостей от конфигурации/окружения.
"""

from __future__ import annotations

import hashlib
from decimal import Decimal

from app.core.constants import MonetaryConstants


def compute_signature(
    account_id: int, amount: Decimal, transaction_id: str, user_id: int, secret_key: str
) -> str:
    """Вычисляет подпись SHA256 для полезной нагрузки вебхука.

    Формула: ``{account_id}{amount}{transaction_id}{user_id}{secret_key}``.

    Args:
        account_id (int): Идентификатор счёта.
        amount (Decimal): Сумма пополнения.
        transaction_id (str): Внешний идентификатор транзакции.
        user_id (int): Идентификатор пользователя.
        secret_key (str): Секретный ключ подписи.

    Returns:
        str: Подпись SHA256 в hex-представлении.
    """
    normalized_amount = amount.quantize(MonetaryConstants.ONE_CENT)
    payload = f'{account_id}{normalized_amount}{transaction_id}{user_id}{secret_key}'
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()
