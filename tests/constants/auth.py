"""Константы для аутентификации/авторизации в тестах."""

from __future__ import annotations

from app.core.constants import AuthConstants


class TestAuthConstants(AuthConstants):
    """Стандартизированные строковые константы авторизации для тестов."""

    # Дополнительные константы JWT и токенов для тестов
    JWT_EXPIRES_MINUTES_DEFAULT = 60
    JWT_EXPIRES_MINUTES_SHORT = 15
    MIN_TOKEN_LENGTH = 10
    MIN_HASH_LENGTH = 10
    TOKEN_GENERATION_DELAY = 1.1
    LONG_FUTURE_EXP_TS = 9999999999
