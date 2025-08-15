"""Тесты для Pydantic схем счетов - все сценарии."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.account import AccountCreate, AccountPublic
from tests.constants import (
    TestDomainConstraints,
    TestDomainIds,
    TestMonetaryConstants,
    TestNumericConstants,
)


class TestAccountCreate:
    """Тесты для схемы создания счета."""

    def test_schema_valid(self) -> None:
        """Тест валидной схемы создания счета."""
        data = {"user_id": TestDomainIds.TEST_USER_ID}

        account_create = AccountCreate(**data)
        assert account_create.user_id == TestDomainIds.TEST_USER_ID

    def test_negative_user_id(self) -> None:
        """Тест создания счета с отрицательным user_id."""
        account_create = AccountCreate(user_id=TestNumericConstants.NEGATIVE_ONE)
        assert account_create.user_id == TestNumericConstants.NEGATIVE_ONE

    def test_zero_user_id(self) -> None:
        """Тест создания счета с нулевым user_id."""
        account_create = AccountCreate(user_id=TestNumericConstants.COUNT_EMPTY)
        assert account_create.user_id == TestNumericConstants.COUNT_EMPTY

    def test_very_large_user_id(self) -> None:
        """Тест создания счета с очень большим user_id."""
        large_user_id = TestDomainConstraints.MAX_INT32
        account_create = AccountCreate(user_id=large_user_id)
        assert account_create.user_id == large_user_id

    def test_missing_user_id(self) -> None:
        """Тест создания счета без user_id."""
        with pytest.raises(ValidationError):
            AccountCreate()  # type: ignore[call-arg]

    def test_invalid_user_id_type(self) -> None:
        """Тест создания счета с невалидным типом user_id."""
        with pytest.raises(ValidationError):
            AccountCreate(user_id="invalid")  # type: ignore[arg-type]

    def test_float_user_id(self) -> None:
        """Тест создания счета с float user_id."""
        account_create = AccountCreate(user_id=TestNumericConstants.FLOAT_42)  # type: ignore[arg-type]
        assert account_create.user_id == TestNumericConstants.INT_42


class TestAccountPublic:
    """Тесты для публичной схемы счета."""

    def test_schema_valid(self) -> None:
        """Тест валидной публичной схемы счета."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "user_id": TestDomainIds.TEST_USER_ID,
            "balance": TestMonetaryConstants.AMOUNT_100_50,
        }

        account_public = AccountPublic(**data)
        assert account_public.id == TestDomainIds.TEST_USER_ID
        assert account_public.user_id == TestDomainIds.TEST_USER_ID
        assert account_public.balance == TestMonetaryConstants.AMOUNT_100_50

    def test_zero_balance(self) -> None:
        """Тест схемы с нулевым балансом."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "user_id": TestDomainIds.TEST_USER_ID,
            "balance": TestMonetaryConstants.AMOUNT_0_00,
        }

        account_public = AccountPublic(**data)
        assert account_public.balance == TestMonetaryConstants.AMOUNT_0_00

    def test_negative_balance(self) -> None:
        """Тест валидации отрицательного баланса."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "user_id": TestDomainIds.TEST_USER_ID,
            "balance": TestMonetaryConstants.AMOUNT_NEG_10_00,
        }

        with pytest.raises(ValidationError) as exc_info:
            AccountPublic(**data)

        errors = exc_info.value.errors()
        assert any(
            "greater than or equal to 0" in str(error["msg"]) for error in errors
        )

    def test_very_large_balance(self) -> None:
        """Тест схемы с очень большим балансом."""
        large_balance = TestMonetaryConstants.AMOUNT_999999999999999_99
        account_public = AccountPublic(
            id=TestDomainIds.TEST_USER_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            balance=large_balance,
        )
        assert account_public.balance == large_balance

    def test_high_precision_balance(self) -> None:
        """Тест схемы с высокой точностью баланса (нормализация до 2 знаков)."""
        precise_balance = TestMonetaryConstants.PRECISE_123_123456789
        account_public = AccountPublic(
            id=TestDomainIds.TEST_USER_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            balance=precise_balance,
        )
        assert account_public.balance == TestMonetaryConstants.AMOUNT_123_12

    def test_string_balance(self) -> None:
        """Тест схемы со строковым представлением баланса."""
        account_public = AccountPublic(
            id=TestDomainIds.TEST_USER_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            balance=TestMonetaryConstants.AMOUNT_123_45_STR,  # type: ignore[arg-type]
        )
        assert account_public.balance == TestMonetaryConstants.AMOUNT_123_45

    def test_invalid_balance(self) -> None:
        """Тест схемы с невалидным балансом."""
        with pytest.raises(ValidationError):
            AccountPublic(
                id=TestDomainIds.TEST_USER_ID,
                user_id=TestDomainIds.TEST_USER_ID,
                balance="invalid",  # type: ignore[arg-type]
            )

    def test_missing_required_fields(self) -> None:
        """Тест схемы с отсутствующими обязательными полями."""
        with pytest.raises(ValidationError):
            AccountPublic(
                user_id=TestDomainIds.TEST_USER_ID,
                balance=TestMonetaryConstants.AMOUNT_100_00,
            )  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            AccountPublic(
                id=TestDomainIds.TEST_USER_ID,
                balance=TestMonetaryConstants.AMOUNT_100_00,
            )  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            AccountPublic(
                id=TestDomainIds.TEST_USER_ID,
                user_id=TestDomainIds.TEST_USER_ID,
            )  # type: ignore[call-arg]

    def test_negative_id(self) -> None:
        """Тест схемы с отрицательным ID."""
        account_public = AccountPublic(
            id=TestNumericConstants.NEGATIVE_ONE,
            user_id=TestDomainIds.TEST_USER_ID,
            balance=TestMonetaryConstants.AMOUNT_100_00,
        )
        assert account_public.id == TestNumericConstants.NEGATIVE_ONE
