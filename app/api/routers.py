"""Единая точка управления всеми роутерами API.

Этот модуль объединяет все версии API и их роутеры.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_v1_router
from app.api.v1.auth import router as auth_v1_router
from app.api.v1.health import router as health_v1_router
from app.api.v1.payments import router as payments_v1_router
from app.api.v1.users import router as users_v1_router
from app.api.v1.webhook import router as webhook_v1_router


def create_api_router() -> APIRouter:
    """Создаёт главный роутер API со всеми версиями.

    Returns:
        APIRouter: Главный роутер с подключенными версиями API.
    """
    api_router = APIRouter()

    # API v1
    api_router.include_router(health_v1_router)
    api_router.include_router(auth_v1_router)
    api_router.include_router(users_v1_router)
    api_router.include_router(accounts_v1_router)
    api_router.include_router(payments_v1_router)
    api_router.include_router(webhook_v1_router)

    return api_router
