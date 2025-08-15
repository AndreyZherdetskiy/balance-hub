"""Общие схемы ответов API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Стандартная схема ошибки.

    Описывает структуру тела ошибки для возврата клиенту.

    Атрибуты:
        detail (str): Текстовое описание ошибки для пользователя/клиента.
    """

    detail: str

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"detail": "Сообщение об ошибке"}]}
    )
