"""Денежные/числовые константы для тестов.

Содержит общие числовые значения для денежных операций в тестах, чтобы избегать
"магических чисел" и обеспечивать единый масштаб представления.
"""

from __future__ import annotations

from decimal import Decimal

from app.core.constants import MonetaryConstants


class TestMonetaryConstants(MonetaryConstants):
    """Константы денежных значений для тестов.

    Используйте эти значения вместо литералов, чтобы избежать ошибок округления
    и обеспечить единообразие масштаба в тестах.
    """

    # Базовые суммы
    AMOUNT_0_00: Decimal = Decimal("0.00")
    AMOUNT_0_01: Decimal = Decimal("0.01")
    AMOUNT_0_99: Decimal = Decimal("0.99")

    # Малые суммы
    AMOUNT_10_00: Decimal = Decimal("10.00")
    AMOUNT_10_01: Decimal = Decimal("10.01")
    AMOUNT_15_99: Decimal = Decimal("15.99")
    AMOUNT_20_00: Decimal = Decimal("20.00")
    AMOUNT_25_00: Decimal = Decimal("25.00")
    AMOUNT_25_50: Decimal = Decimal("25.50")
    AMOUNT_26_00: Decimal = Decimal("26.00")
    AMOUNT_30_00: Decimal = Decimal("30.00")

    # Средние суммы
    AMOUNT_50_25: Decimal = Decimal("50.25")
    AMOUNT_75_00: Decimal = Decimal("75.00")
    AMOUNT_99_99: Decimal = Decimal("99.99")
    AMOUNT_100_00: Decimal = Decimal("100.00")
    AMOUNT_100_01: Decimal = Decimal("100.01")
    AMOUNT_100_50: Decimal = Decimal("100.50")
    AMOUNT_100_99: Decimal = Decimal("100.99")
    AMOUNT_123_12: Decimal = Decimal("123.12")
    AMOUNT_123_45: Decimal = Decimal("123.45")
    AMOUNT_150_00: Decimal = Decimal("150.00")
    AMOUNT_175_50: Decimal = Decimal("175.50")
    AMOUNT_200_00: Decimal = Decimal("200.00")

    # Большие суммы
    AMOUNT_999999_99: Decimal = Decimal("999999.99")
    AMOUNT_1000000_00: Decimal = Decimal("1000000.00")
    AMOUNT_9999999999_99: Decimal = Decimal("9999999999.99")
    AMOUNT_999999999999999_99: Decimal = Decimal("999999999999999.99")
    AMOUNT_1000000000000000_00: Decimal = Decimal("1000000000000000.00")
    AMOUNT_9999999999999999: Decimal = Decimal("9999999999999999")
    AMOUNT_999999999999999999: Decimal = Decimal("999999999999999999")

    # Отрицательные суммы
    AMOUNT_NEG_10_00: Decimal = Decimal("-10.00")
    AMOUNT_NEG_100_00: Decimal = Decimal("-100.00")

    # Точные значения
    PRECISE_123_123456789: Decimal = Decimal("123.123456789")
    PRECISE_123_123456789123456: Decimal = Decimal("123.123456789123456")

    # Специальные форматы
    AMOUNT_100_0: Decimal = Decimal("100.0")
    AMOUNT_100_000: Decimal = Decimal("100.000")

    # Строковые представления
    AMOUNT_123_45_STR: str = "123.45"
    AMOUNT_99_99_STR: str = "99.99"
