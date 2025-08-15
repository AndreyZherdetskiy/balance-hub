"""Единые ограничения для полей моделей и валидации API для тестов.

Этот модуль содержит все ограничения для полей, используемые как в ORM моделях,
так и в Pydantic схемах. Обеспечивает консистентность между уровнем БД и API.
"""

from __future__ import annotations

from app.core.constants import FieldConstraints


class TestFieldConstraints(FieldConstraints):
    """Единые ограничения для полей моделей и валидации API для тестов."""

    # Дополнительные константы длины строк для тестов
    LONG_MESSAGE_LENGTH: int = 1000
    LONG_NAME_LENGTH: int = 200
    LONG_EMAIL_LOCAL_LENGTH: int = 100
    LONG_EMAIL_LOCAL_LENGTH_LARGE: int = 300
    LONG_NAME_LENGTH_LARGE: int = 1000
