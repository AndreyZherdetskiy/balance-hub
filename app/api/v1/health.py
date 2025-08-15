"""Эндпойнты healthcheck приложения и БД."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import (
    ApiDescription,
    ApiErrorResponses,
    ApiSuccessResponses,
    ApiSummary,
    HealthPaths,
)
from app.core.errors import ServiceUnavailableError, to_http_exc
from app.db.session import get_db_session


router = APIRouter(prefix=HealthPaths.PREFIX, tags=[HealthPaths.TAG])


@router.get(
    HealthPaths.HEALTH,
    summary=ApiSummary.HEALTH_APP,
    description=ApiDescription.HEALTH_APP,
    status_code=status.HTTP_200_OK,
    responses={200: ApiSuccessResponses.HEALTH_APP_200},
)
async def health_app() -> dict:
    """Проверяет доступность приложения.

    Returns:
        dict: Краткая информация о состоянии приложения c именем и режимом `debug`.
    """
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "debug": settings.debug}


@router.get(
    HealthPaths.HEALTH_DB,
    summary=ApiSummary.HEALTH_DB,
    description=ApiDescription.HEALTH_DB,
    status_code=status.HTTP_200_OK,
    responses={
        200: ApiSuccessResponses.HEALTH_DB_200,
        503: ApiErrorResponses.DB_CONNECTION_ERROR,
    },
)
async def health_db(db: AsyncSession = Depends(get_db_session)) -> dict:
    """Проверяет доступность базы данных простым запросом `SELECT 1`.

    Args:
        db (AsyncSession): Асинхронная сессия БД.

    Returns:
        dict: Статус подключения к базе данных.

    Raises:
        HTTPException: 503 если подключение к БД недоступно.
    """
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - в health допускается широкий перехват
        http_exc = to_http_exc(ServiceUnavailableError())
        raise http_exc from exc
    return {"status": "ok"}
