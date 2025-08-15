"""Тесты для API health check."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import (
    TestHealthPaths,
    TestAuthData,
    TestApiSuccessResponses,
    TestValidationData,
)


class TestHealthApi:
    """Тесты health эндпоинтов."""

    @pytest.mark.asyncio()
    async def test_health_app(self, client: AsyncClient) -> None:
        """Базовая проверка доступности приложения."""
        path = f"{TestHealthPaths.PREFIX}{TestHealthPaths.HEALTH}"
        resp = await client.get(path)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["status"] == TestApiSuccessResponses.STATUS_OK
        assert "app" in body
        assert "debug" in body
        assert isinstance(body["debug"], bool)

    @pytest.mark.asyncio()
    async def test_health_db(self, client: AsyncClient) -> None:
        """Проверка подключения к БД."""
        path = f"{TestHealthPaths.PREFIX}{TestHealthPaths.HEALTH_DB}"
        resp = await client.get(path)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["status"] == TestApiSuccessResponses.STATUS_OK

    @pytest.mark.asyncio()
    async def test_health_db_unavailable(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """При ошибке выполнения запроса возвращаем 503 (ветка исключения)."""
        from sqlalchemy.ext.asyncio import AsyncSession

        async def fail_execute(self: AsyncSession, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise RuntimeError(TestValidationData.ROOT_CAUSE_MESSAGE)

        monkeypatch.setattr(AsyncSession, "execute", fail_execute, raising=True)

        path = f"{TestHealthPaths.PREFIX}{TestHealthPaths.HEALTH_DB}"
        resp = await client.get(path)
        assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    @pytest.mark.asyncio()
    async def test_health_endpoints_no_auth_required(self, client: AsyncClient) -> None:
        """Эндпоинты health не требуют авторизации."""
        health = f"{TestHealthPaths.PREFIX}{TestHealthPaths.HEALTH}"
        health_db = f"{TestHealthPaths.PREFIX}{TestHealthPaths.HEALTH_DB}"

        resp1 = await client.get(health)
        assert resp1.status_code == status.HTTP_200_OK

        resp2 = await client.get(health_db)
        assert resp2.status_code == status.HTTP_200_OK

        headers = {
            TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{TestAuthData.INVALID_TOKEN}"
        }
        resp3 = await client.get(health, headers=headers)
        assert resp3.status_code == status.HTTP_200_OK

        resp4 = await client.get(health_db, headers=headers)
        assert resp4.status_code == status.HTTP_200_OK
