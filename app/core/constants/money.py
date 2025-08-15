"""Денежные/числовые константы."""

from __future__ import annotations

from decimal import Decimal


class MonetaryConstants:
    """Константы денежных значений.

    Используйте эти значения вместо литералов, чтобы избежать ошибок округления
    и обеспечить единообразие масштаба.
    """

    # Точность для денежных значений в БД
    DECIMAL_PRECISION: int = 12
    DECIMAL_SCALE: int = 2

    # Длина текстового представления для хранения денег на SQLite
    MONEY_TEXT_MAX_LENGTH: int = 100

    # Константы значений
    ZERO: Decimal = Decimal("0")
    ZERO_TWO_PLACES: Decimal = Decimal("0.00")
    ONE_CENT: Decimal = Decimal("0.01")
    MAX_DECIMAL_PLACES: int = 2
