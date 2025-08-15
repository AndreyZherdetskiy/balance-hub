"""Пакет DI провайдеров для FastAPI."""

from .auth import get_current_admin, get_current_user
from .crud import get_account_crud, get_payment_crud, get_user_crud
from .policies import require_self_or_admin_user
from .services import (
    get_account_service,
    get_auth_service,
    get_payment_service,
    get_user_service,
    get_webhook_service,
)
from .validators import get_user_async_validator


__all__ = [
    "get_current_admin",
    "get_current_user",
    "get_account_crud",
    "get_payment_crud",
    "get_user_crud",
    "get_account_service",
    "get_auth_service",
    "get_payment_service",
    "get_user_service",
    "get_webhook_service",
    "get_user_async_validator",
    "require_self_or_admin_user",
]
