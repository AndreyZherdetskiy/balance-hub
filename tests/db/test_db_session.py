"""Тесты провайдера БД-сессии и инициализации движка."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.session import get_db_session


class TestDbSession:
    """Тесты провайдера БД-сессии и инициализации движка."""

    @pytest.mark.asyncio()
    async def test_get_db_session_yields_session(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Провайдер возвращает живую сессию, совместимую с AsyncSession."""
        # Используем тестовое приложение, где зависимость переопределена на тестовую БД
        async for session in get_db_session():  # type: ignore[misc]
            assert isinstance(session, AsyncSession)
