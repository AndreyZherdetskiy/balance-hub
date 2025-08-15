"""Pytest фикстуры для приложения BalanceHub.

Содержит:
- создание изолированной async SQLite БД на каждый тест
- переопределение зависимости `get_db_session`
- фабрику FastAPI-приложения
- HTTP-клиент для интеграционных тестов
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.models import account as _account_model  # noqa: F401
from app.models import payment as _payment_model  # noqa: F401

# Импорт моделей, чтобы таблицы попали в metadata
from app.models import user as _user_model  # noqa: F401


@pytest.fixture()
def test_db_url(tmp_path: Path) -> str:
    """URL тестовой SQLite БД (файл), уникальный на тест.

    Args:
        tmp_path: Временная директория pytest.

    Returns:
        str: DSN для async SQLite.
    """
    return f"sqlite+aiosqlite:///{tmp_path}/test.db"


@pytest.fixture()
async def test_sessionmaker(
    test_db_url: str,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Создать движок и фабрику сессий для тестовой БД, создать схемы.

    Args:
        test_db_url: DSN для БД.

    Yields:
        async_sessionmaker: Фабрика сессий.
    """
    engine = create_async_engine(test_db_url, future=True)
    async_session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield async_session_factory
    finally:
        # Чистим схему и закрываем движок
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture()
def test_settings(test_db_url: str) -> Settings:  # type: ignore[name-defined]
    """Создать настройки для тестов.

    Args:
        test_db_url: URL тестовой БД.

    Returns:
        Settings: Тестовые настройки.
    """
    from app.core.config import Settings

    # Создаем настройки напрямую с тестовыми значениями
    from tests.constants import TestAuthConstants, TestUserData, TestValidationData

    return Settings(
        app_name=TestUserData.TEST_APP_NAME,
        env="test",
        debug=True,
        cors_origins=[TestValidationData.CORS_WILDCARD],
        jwt_secret=TestUserData.JWT_SECRET_TEST,
        jwt_algorithm=TestUserData.TEST_JWT_ALGORITHM,
        jwt_expires_minutes=TestAuthConstants.JWT_EXPIRES_MINUTES_DEFAULT,
        webhook_secret_key=TestUserData.TEST_WEBHOOK_SECRET,
        database_url=test_db_url,
        sync_database_url=test_db_url.replace("+aiosqlite", ""),
    )


@pytest.fixture()
def make_token(test_settings: Settings) -> callable:  # type: ignore[name-defined,type-arg]
    """Создать функцию для генерации тестовых токенов.

    Args:
        test_settings: Тестовые настройки.

    Returns:
        callable: Функция для создания токенов.
    """
    from app.core.security import create_access_token

    def _make_token(user_id: int) -> str:
        """Создать токен для пользователя используя тестовые настройки."""
        return create_access_token(
            user_id,
            test_settings.jwt_secret,
            test_settings.jwt_algorithm,
            test_settings.jwt_expires_minutes,
        )

    return _make_token


@pytest.fixture()
def app(
    monkeypatch: pytest.MonkeyPatch,
    test_db_url: str,
    test_sessionmaker: async_sessionmaker[AsyncSession],
    test_settings: Settings,
) -> FastAPI:  # type: ignore[name-defined]
    """Создать экземпляр тестового FastAPI приложения с переопределённой БД.

    Переопределяет `get_db_session` и `get_settings` для использования тестовых значений.
    Устанавливает необходимые переменные окружения до импорта приложения.

    Args:
        monkeypatch: Фикстура pytest для патча окружения.
        test_db_url: DSN тестовой БД.
        test_sessionmaker: Фабрика сессий для БД.
        test_settings: Тестовые настройки.

    Returns:
        FastAPI: Инициализированное тестовое приложение.
    """
    # Обязательные переменные окружения для Settings (для совместимости)
    monkeypatch.setenv("DATABASE_URL", test_db_url)
    from tests.constants import TestUserData, TestValidationData

    monkeypatch.setenv("JWT_SECRET", TestUserData.JWT_SECRET_TEST)
    monkeypatch.setenv("WEBHOOK_SECRET_KEY", TestUserData.TEST_WEBHOOK_SECRET)
    monkeypatch.setenv("CORS_ORIGINS", TestValidationData.CORS_WILDCARD)

    # Создаём приложение ПОСЛЕ установки окружения
    # Импорт и создание приложения выполняем ПОСЛЕ установки окружения
    from app.main import create_app

    application = create_app()

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with test_sessionmaker() as session:
            yield session

    def override_get_settings() -> Settings:
        return test_settings

    application.dependency_overrides[get_db_session] = override_get_db_session
    application.dependency_overrides[get_settings] = override_get_settings
    return application


@pytest.fixture()
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP-клиент для интеграционных тестов поверх ASGI.

    Args:
        app: Тестовое FastAPI приложение.

    Yields:
        AsyncClient: HTTP-клиент.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
