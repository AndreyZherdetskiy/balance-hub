"""Тесты для пользовательских типов БД (`SafeMoney`)."""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.dialects.postgresql.psycopg import PGDialect_psycopg
from sqlalchemy.dialects.sqlite.base import SQLiteDialect

from app.db.types import SafeMoney
from tests.constants import TestMonetaryConstants


class DummyDescriptor:
    """Мок-дескриптор для тестирования."""

    def __init__(self, name: str) -> None:
        """Инициализация мок-дескриптора."""
        self.name = name


class DummyDialect(SQLiteDialect):
    """Мок-диалект для тестирования."""

    def __init__(self, name: str) -> None:
        """Инициализация мок-диалекта."""
        super().__init__()
        self.name = name

    def type_descriptor(self, type_):  # type: ignore[override]
        """Возвращает мок-дескриптор для типа."""
        return DummyDescriptor(self.name)


@pytest.mark.parametrize(
    "dialect, expected_name",
    [
        (DummyDialect("sqlite"), "sqlite"),
        (PGDialect_psycopg(), "postgresql"),
    ],
)
def test_load_dialect_impl_returns_expected_descriptor(dialect, expected_name) -> None:  # type: ignore[no-untyped-def]
    sm = SafeMoney()
    desc = sm.load_dialect_impl(dialect)
    # Для sqlite мы вернули DummyDescriptor; для PG — Numeric descriptor
    if expected_name == "sqlite":
        assert isinstance(desc, DummyDescriptor)
        assert desc.name == "sqlite"
    else:
        # У PG это уже не DummyDescriptor; проверим наличие атрибутов precision/scale косвенно
        assert hasattr(desc, "scale") or hasattr(desc, "asdecimal")


def test_process_bind_param_sqlite_str_format() -> None:
    sm = SafeMoney()
    dialect = DummyDialect("sqlite")
    result = sm.process_bind_param(TestMonetaryConstants.AMOUNT_123_45, dialect)
    assert isinstance(result, str)
    assert result == f"{TestMonetaryConstants.AMOUNT_123_45:.2f}"


def test_process_bind_param_pg_returns_decimal() -> None:
    sm = SafeMoney()
    dialect = PGDialect_psycopg()
    result = sm.process_bind_param(TestMonetaryConstants.AMOUNT_123_45, dialect)
    assert isinstance(result, Decimal)
    assert result == TestMonetaryConstants.AMOUNT_123_45


def test_process_bind_param_none_passthrough() -> None:
    sm = SafeMoney()
    dialect = DummyDialect("sqlite")
    assert sm.process_bind_param(None, dialect) is None


def test_process_result_value_sqlite_parses_decimal() -> None:
    sm = SafeMoney()
    dialect = DummyDialect("sqlite")
    result = sm.process_result_value(str(TestMonetaryConstants.AMOUNT_100_00), dialect)
    assert isinstance(result, Decimal)
    assert result == TestMonetaryConstants.AMOUNT_100_00


def test_process_result_value_pg_passthrough_decimal() -> None:
    sm = SafeMoney()
    dialect = PGDialect_psycopg()
    result = sm.process_result_value(TestMonetaryConstants.AMOUNT_100_00, dialect)
    assert isinstance(result, Decimal)
    assert result == TestMonetaryConstants.AMOUNT_100_00


def test_process_result_value_none_passthrough() -> None:
    sm = SafeMoney()
    dialect = DummyDialect("sqlite")
    assert sm.process_result_value(None, dialect) is None
