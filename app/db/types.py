"""Пользовательские типы SQLAlchemy.

Содержит безопасный тип для денежных значений, который предотвращает потерю
точности на SQLite, сохраняя `Decimal` в текстовом виде и преобразуя его при
чтении. Для остальных СУБД используется нативный `NUMERIC` с заданной
точностью и масштабом.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.types import Numeric, String, TypeDecorator

from app.core.constants.money import MonetaryConstants


class SafeMoney(TypeDecorator):
    """Безопасный тип хранения денег для разных СУБД.

    - На SQLite хранит значения как TEXT, чтобы избежать приведения к float и
      нежелательного округления.
    - На остальных СУБД использует `NUMERIC(precision, scale, asdecimal=True)`.
    """

    cache_ok = True
    impl = Numeric

    def load_dialect_impl(self, dialect):
        """Загружает реализацию типа для конкретной СУБД.

        Args:
            dialect: Диалект SQLAlchemy для СУБД.

        Returns:
            TypeDescriptor: Реализация типа для СУБД.
        """
        if dialect.name == "sqlite":
            return dialect.type_descriptor(
                String(MonetaryConstants.MONEY_TEXT_MAX_LENGTH)
            )
        return dialect.type_descriptor(
            Numeric(
                MonetaryConstants.DECIMAL_PRECISION,
                MonetaryConstants.DECIMAL_SCALE,
                asdecimal=True,
            )
        )

    def process_bind_param(self, value, dialect):
        """Обрабатывает параметр при привязке к запросу.

        Args:
            value: Значение для привязки.
            dialect: Диалект SQLAlchemy для СУБД.

        Returns:
            Обработанное значение для привязки.
        """
        if value is None:
            return None
        quantized = Decimal(value).quantize(MonetaryConstants.ONE_CENT)
        if dialect.name == "sqlite":
            return format(quantized, "f")
        return quantized

    def process_result_value(self, value, dialect):
        """Обрабатывает значение при получении из БД.

        Args:
            value: Значение из БД.
            dialect: Диалект SQLAlchemy для СУБД.

        Returns:
            Обработанное значение для Python.
        """
        if value is None:
            return None
        if dialect.name == "sqlite":
            return Decimal(value)
        return value
