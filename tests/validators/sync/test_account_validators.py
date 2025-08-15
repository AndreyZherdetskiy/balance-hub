"""Тесты для синхронных валидаторов счетов."""

from __future__ import annotations

import pytest
from decimal import Decimal

from app.core.constants import ErrorMessages
from tests.constants import (
    TestMonetaryConstants,
    TestNumericConstants,
    TestDomainIds,
    TestPaginationParams,
)
from app.core.errors import ValidationError
from app.validators.sync.accounts import AccountValidator


class TestAccountValidator:
    """Тесты для AccountValidator."""

    @pytest.fixture
    def validator(self) -> AccountValidator:
        """Создает экземпляр AccountValidator."""
        return AccountValidator()

    def test_validate_user_id_valid(self, validator: AccountValidator) -> None:
        """Тест валидации корректного ID пользователя."""
        validator.validate_user_id(TestDomainIds.TEST_USER_ID)
        validator.validate_user_id(TestDomainIds.NONEXISTENT_USER_ID)

    def test_validate_user_id_invalid(self, validator: AccountValidator) -> None:
        """Тест валидации некорректного ID пользователя."""
        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id(TestNumericConstants.COUNT_EMPTY)

        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id(TestNumericConstants.NEGATIVE_ONE)

    def test_validate_balance_valid(self, validator: AccountValidator) -> None:
        """Тест валидации корректного баланса."""
        validator.validate_balance(TestMonetaryConstants.AMOUNT_0_00)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_100_50)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_999999_99)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_1000000_00)

    def test_validate_balance_invalid(self, validator: AccountValidator) -> None:
        """Тест валидации некорректного баланса."""
        with pytest.raises(
            ValidationError, match=ErrorMessages.BALANCE_CANNOT_BE_NEGATIVE
        ):
            validator.validate_balance(-TestMonetaryConstants.AMOUNT_0_01)

        with pytest.raises(
            ValidationError, match=ErrorMessages.BALANCE_CANNOT_BE_NEGATIVE
        ):
            validator.validate_balance(TestMonetaryConstants.AMOUNT_NEG_100_00)

    def test_validate_balance_edge_cases(self, validator: AccountValidator) -> None:
        """Тест граничных случаев баланса."""
        validator.validate_balance(TestMonetaryConstants.AMOUNT_0_00)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_1000000_00)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_0_01)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_0_99)

    def test_validate_balance_precision(self, validator: AccountValidator) -> None:
        """Тест точности баланса."""
        validator.validate_balance(TestMonetaryConstants.AMOUNT_100_00)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_100_01)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_100_99)
        validator.validate_balance(Decimal(100))
        validator.validate_balance(TestMonetaryConstants.AMOUNT_0_00)

    def test_validate_balance_too_many_decimals(
        self, validator: AccountValidator
    ) -> None:
        """Баланс с более чем двумя знаками после запятой должен падать."""
        with pytest.raises(ValidationError, match=ErrorMessages.BALANCE_MAX_2_DECIMALS):
            validator.validate_balance(Decimal("100.001"))

    def test_validate_user_id_boundaries(self, validator: AccountValidator) -> None:
        """Тест граничных значений ID пользователя."""
        validator.validate_user_id(TestDomainIds.TEST_USER_ID)
        with pytest.raises(ValidationError):
            validator.validate_user_id(TestNumericConstants.COUNT_EMPTY)

    def test_validate_balance_boundaries(self, validator: AccountValidator) -> None:
        """Тест граничных значений баланса."""
        validator.validate_balance(TestMonetaryConstants.AMOUNT_0_00)
        with pytest.raises(ValidationError):
            validator.validate_balance(-TestMonetaryConstants.ONE_CENT)

    def test_validate_user_id_type_error(self, validator: AccountValidator) -> None:
        """Тест ошибки типа для ID пользователя."""
        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id("invalid")

        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id(1.5)

        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id(None)

    def test_validate_balance_type_error(self, validator: AccountValidator) -> None:
        """Тест ошибки типа для баланса."""
        with pytest.raises(
            ValidationError, match=ErrorMessages.BALANCE_MUST_BE_DECIMAL
        ):
            validator.validate_balance("invalid")

        with pytest.raises(
            ValidationError, match=ErrorMessages.BALANCE_MUST_BE_DECIMAL
        ):
            validator.validate_balance(100)

        with pytest.raises(
            ValidationError, match=ErrorMessages.BALANCE_MUST_BE_DECIMAL
        ):
            validator.validate_balance(None)

    def test_validate_user_id_negative_values(
        self, validator: AccountValidator
    ) -> None:
        """Тест отрицательных значений ID пользователя."""
        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id(TestNumericConstants.NEGATIVE_ONE)

        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id(-100)

        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id(-TestDomainIds.NONEXISTENT_USER_ID)

    def test_validate_balance_negative_values(
        self, validator: AccountValidator
    ) -> None:
        """Тест отрицательных значений баланса."""
        with pytest.raises(
            ValidationError, match=ErrorMessages.BALANCE_CANNOT_BE_NEGATIVE
        ):
            validator.validate_balance(-TestMonetaryConstants.AMOUNT_0_01)

        with pytest.raises(
            ValidationError, match=ErrorMessages.BALANCE_CANNOT_BE_NEGATIVE
        ):
            validator.validate_balance(TestMonetaryConstants.AMOUNT_NEG_100_00)

        with pytest.raises(
            ValidationError, match=ErrorMessages.BALANCE_CANNOT_BE_NEGATIVE
        ):
            validator.validate_balance(-TestMonetaryConstants.AMOUNT_999999_99)

    def test_validate_user_id_zero(self, validator: AccountValidator) -> None:
        """Тест нулевого значения ID пользователя."""
        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_USER_ID):
            validator.validate_user_id(TestNumericConstants.COUNT_EMPTY)

    def test_validate_balance_zero(self, validator: AccountValidator) -> None:
        """Тест нулевого значения баланса."""
        validator.validate_balance(TestMonetaryConstants.AMOUNT_0_00)
        validator.validate_balance(TestMonetaryConstants.AMOUNT_0_00)

    def test_validate_pagination_params_valid(
        self, validator: AccountValidator
    ) -> None:
        """Тест валидации корректных параметров пагинации."""
        validator.validate_pagination_params(
            TestPaginationParams.VALID_LIMIT_10, TestPaginationParams.VALID_OFFSET_0
        )
        validator.validate_pagination_params(
            TestPaginationParams.VALID_LIMIT_100, TestPaginationParams.VALID_OFFSET_50
        )
        validator.validate_pagination_params(
            TestPaginationParams.VALID_LIMIT_MIN, TestPaginationParams.VALID_OFFSET_0
        )

    def test_validate_pagination_params_invalid_limit(
        self, validator: AccountValidator
    ) -> None:
        """Тест валидации некорректного лимита пагинации."""
        with pytest.raises(ValidationError, match=ErrorMessages.LIMIT_RANGE_INVALID):
            validator.validate_pagination_params(
                TestNumericConstants.COUNT_EMPTY, TestNumericConstants.COUNT_EMPTY
            )

        with pytest.raises(ValidationError, match=ErrorMessages.LIMIT_RANGE_INVALID):
            validator.validate_pagination_params(
                TestPaginationParams.INVALID_LIMIT_NEGATIVE,
                TestNumericConstants.COUNT_EMPTY,
            )

        with pytest.raises(ValidationError, match=ErrorMessages.LIMIT_RANGE_INVALID):
            validator.validate_pagination_params(
                TestPaginationParams.INVALID_LIMIT_TOO_LARGE,
                TestNumericConstants.COUNT_EMPTY,
            )

    def test_validate_pagination_params_invalid_offset(
        self, validator: AccountValidator
    ) -> None:
        """Тест валидации некорректного смещения пагинации."""
        with pytest.raises(
            ValidationError, match=ErrorMessages.OFFSET_MUST_BE_NON_NEGATIVE
        ):
            validator.validate_pagination_params(
                TestPaginationParams.VALID_LIMIT_10,
                TestPaginationParams.INVALID_OFFSET_NEGATIVE,
            )

        with pytest.raises(
            ValidationError, match=ErrorMessages.OFFSET_MUST_BE_NON_NEGATIVE
        ):
            validator.validate_pagination_params(
                TestPaginationParams.VALID_LIMIT_10, -100
            )
