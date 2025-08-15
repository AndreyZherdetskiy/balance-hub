from __future__ import annotations

from decimal import Decimal

from app.core.constants import (
    DomainConstraints,
    ErrorMessages,
    MonetaryConstants,
    PaginationParams,
)
from app.core.errors import ValidationError


class AccountValidator:
    """Валидатор данных счётов."""

    @staticmethod
    def validate_user_id(user_id: int) -> None:
        """Проверяет корректность идентификатора пользователя.

        Args:
            user_id (int): Идентификатор пользователя для проверки.

        Raises:
            ValidationError: Если идентификатор некорректен.
        """
        if not isinstance(user_id, int) or user_id < DomainConstraints.MIN_ID:
            raise ValidationError(ErrorMessages.INVALID_USER_ID)

    @staticmethod
    def validate_pagination_params(limit: int, offset: int) -> None:
        """Проверяет параметры пагинации.

        Args:
            limit (int): Лимит записей.
            offset (int): Смещение.

        Raises:
            ValidationError: Если параметры некорректны.
        """
        if (
            not isinstance(limit, int)
            or limit < PaginationParams.MIN_LIMIT
            or limit > PaginationParams.MAX_LIMIT
        ):
            raise ValidationError(ErrorMessages.LIMIT_RANGE_INVALID)

        if not isinstance(offset, int) or offset < PaginationParams.DEFAULT_OFFSET:
            raise ValidationError(ErrorMessages.OFFSET_MUST_BE_NON_NEGATIVE)

    @staticmethod
    def validate_balance(balance: Decimal) -> None:
        """Проверяет корректность баланса счёта.

        Args:
            balance (Decimal): Баланс для проверки.

        Raises:
            ValidationError: Если баланс некорректен.
        """
        if not isinstance(balance, Decimal):
            raise ValidationError(ErrorMessages.BALANCE_MUST_BE_DECIMAL)

        if balance < MonetaryConstants.ZERO:
            raise ValidationError(ErrorMessages.BALANCE_CANNOT_BE_NEGATIVE)

        if balance.as_tuple().exponent < -MonetaryConstants.MAX_DECIMAL_PLACES:
            raise ValidationError(ErrorMessages.BALANCE_MAX_2_DECIMALS)
