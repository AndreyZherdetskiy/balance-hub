"""Pydantic-схемы для счетов."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants.money import MonetaryConstants


class AccountBase(BaseModel):
    """Базовые поля счёта."""

    balance: Decimal = Field(ge=MonetaryConstants.ZERO)

    @field_validator("balance")
    @classmethod
    def normalize_balance(cls, v: Decimal) -> Decimal:
        """Нормализует баланс до двух знаков после запятой.

        Args:
            v (Decimal): Входное значение баланса.

        Returns:
            Decimal: Нормализованное значение с точностью до копеек.
        """
        return v.quantize(MonetaryConstants.ONE_CENT)


class AccountCreate(BaseModel):
    """Схема создания счёта (админ или вебхук)."""

    user_id: int

    model_config = ConfigDict(json_schema_extra={"examples": [{"user_id": 1}]})


class AccountPublic(AccountBase):
    """Публичное представление счёта."""

    id: int
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"id": 1, "user_id": 1, "balance": "100.00"}]},
    )
