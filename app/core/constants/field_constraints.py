"""Единые ограничения для полей моделей и валидации API.

Этот модуль содержит все ограничения для полей, используемые как в ORM моделях,
так и в Pydantic схемах. Обеспечивает консистентность между уровнем БД и API.
"""

from __future__ import annotations


class FieldConstraints:
    """Единые ограничения для полей моделей и валидации API."""

    # Транзакции
    TRANSACTION_ID_MIN_LENGTH: int = 1
    TRANSACTION_ID_MAX_LENGTH: int = 64  # UUID + дополнительные символы

    # Пользователь
    USER_EMAIL_MIN_LENGTH: int = 5  # a@b.c
    USER_EMAIL_MAX_LENGTH: int = 254  # RFC 5321 стандарт
    USER_FULL_NAME_MIN_LENGTH: int = 2  # Минимум 2 символа для имени
    USER_FULL_NAME_MAX_LENGTH: int = 100  # Реалистичная длина для полного имени
    PASSWORD_MIN_LENGTH: int = 8  # Минимум для безопасности
    PASSWORD_MAX_LENGTH: int = 128  # Максимум для хеша bcrypt
    HASHED_PASSWORD_MAX_LENGTH: int = 60  # bcrypt хеш всегда 60 символов
