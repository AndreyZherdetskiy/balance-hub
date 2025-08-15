"""Единые константы путей API."""

from __future__ import annotations


class ApiPrefixes:
    """Префиксы версий и разделов API."""

    API_V1 = '/api/v1'


class AuthPaths:
    """Пути для auth-эндпойнтов."""

    PREFIX = f'{ApiPrefixes.API_V1}/auth'
    LOGIN = '/login'
    TOKEN_URL = f'{PREFIX}{LOGIN}'
    TAG = 'auth'


class WebhookPaths:
    """Пути для webhook-эндпойнтов."""

    PREFIX = f'{ApiPrefixes.API_V1}/webhook'
    TAG = 'webhook'
    PAYMENT = '/payment'


class UsersPaths:
    """Константы API пользователей (админ и профиль)."""

    PREFIX = ApiPrefixes.API_V1
    TAG = 'users'
    ME = '/users/me'
    ADMIN_USERS = '/admin/users'
    ADMIN_USER_ID = '/admin/users/{user_id}'


class AccountsPaths:
    """Константы API счетов."""

    PREFIX = ApiPrefixes.API_V1
    TAG = 'accounts'
    USERS_ACCOUNTS = '/users/{user_id}/accounts'
    ADMIN_USERS_ACCOUNTS = '/admin/users/{user_id}/accounts'


class PaymentsPaths:
    """Константы API платежей."""

    PREFIX = ApiPrefixes.API_V1
    TAG = 'payments'
    LIST = '/payments'


class HealthPaths:
    """Константы API healthcheck."""

    PREFIX = ApiPrefixes.API_V1
    TAG = 'health'
    HEALTH = '/health'
    HEALTH_DB = '/health/db'
