"""Единые константы путей API для тестов.

Централизует формирование путей и префиксов для тестов, чтобы избежать рассинхронизации
между зависимостями (напр. OAuth2 tokenUrl) и реальными роутерами.
"""

from __future__ import annotations

from app.core.constants import (
    AccountsPaths,
    ApiPrefixes,
    AuthPaths,
    HealthPaths,
    PaymentsPaths,
    UsersPaths,
    WebhookPaths,
)


class TestApiPrefixes(ApiPrefixes):
    """Префиксы версий и разделов API для тестов."""


class TestHealthPaths(HealthPaths):
    """Константы API healthcheck для тестов."""


class TestAuthPaths(AuthPaths):
    """Пути для auth-эндпойнтов в тестах."""


class TestUsersPaths(UsersPaths):
    """Константы API пользователей для тестов (админ и профиль)."""

    # Дополнительные префиксы разделов для удобных проверок маршрутов на уровне роутера
    USERS_PREFIX = f"{TestApiPrefixes.API_V1}/users"
    ADMIN_PREFIX = f"{TestApiPrefixes.API_V1}/admin"


class TestAccountsPaths(AccountsPaths):
    """Константы API счетов для тестов."""


class TestPaymentsPaths(PaymentsPaths):
    """Константы API платежей для тестов."""


class TestWebhookPaths(WebhookPaths):
    """Пути для webhook-эндпойнтов в тестах."""
