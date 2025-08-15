"""Тесты для модели Account - все сценарии."""

from __future__ import annotations

from app.models.account import Account
from tests.constants import (
    TestDomainConstraints,
    TestDomainIds,
    TestMonetaryConstants,
    TestNumericConstants,
)


class TestAccountModel:
    """Тесты модели Account."""

    def test_account_model_creation(self) -> None:
        """Тест создания модели счета."""
        account = Account(
            user_id=TestDomainIds.TEST_USER_ID,
            balance=TestMonetaryConstants.AMOUNT_100_50,
        )

        assert account.user_id == TestDomainIds.TEST_USER_ID
        assert account.balance == TestMonetaryConstants.AMOUNT_100_50

    def test_account_model_default_balance(self) -> None:
        """Тест модели счета с балансом по умолчанию."""
        account = Account(user_id=TestDomainIds.TEST_USER_ID)

        assert (
            account.balance is None
            or account.balance == TestMonetaryConstants.AMOUNT_0_00
        )

    def test_account_model_zero_balance(self) -> None:
        """Тест модели счета с нулевым балансом."""
        account = Account(
            user_id=TestDomainIds.TEST_USER_ID,
            balance=TestMonetaryConstants.AMOUNT_0_00,
        )

        assert account.balance == TestMonetaryConstants.AMOUNT_0_00

    def test_account_model_very_large_balance(self) -> None:
        """Тест модели счета с очень большим балансом."""
        large_balance = TestMonetaryConstants.AMOUNT_9999999999_99
        account = Account(user_id=TestDomainIds.TEST_USER_ID, balance=large_balance)

        assert account.balance == large_balance

    def test_account_model_very_small_balance(self) -> None:
        """Тест модели счета с очень маленьким балансом."""
        small_balance = TestMonetaryConstants.AMOUNT_0_01
        account = Account(user_id=TestDomainIds.TEST_USER_ID, balance=small_balance)

        assert account.balance == small_balance

    def test_account_model_many_decimal_places(self) -> None:
        """Тест модели счета с множественными десятичными знаками."""
        precise_balance = TestMonetaryConstants.PRECISE_123_123456789
        account = Account(user_id=TestDomainIds.TEST_USER_ID, balance=precise_balance)

        assert account.balance == precise_balance

    def test_account_model_negative_user_id(self) -> None:
        """Тест модели счета с отрицательным user_id."""
        account = Account(
            user_id=TestNumericConstants.NEGATIVE_ONE,
            balance=TestMonetaryConstants.AMOUNT_100_00,
        )

        assert account.user_id == TestNumericConstants.NEGATIVE_ONE

    def test_account_model_large_user_id(self) -> None:
        """Тест модели счета с большим user_id."""
        large_user_id = TestDomainConstraints.MAX_INT32
        account = Account(
            user_id=large_user_id, balance=TestMonetaryConstants.AMOUNT_100_00
        )

        assert account.user_id == large_user_id
