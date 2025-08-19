"""Pytest фикстуры для приложения BalanceHub.

Содержит:
- создание изолированной async SQLite БД на каждый тест
- переопределение зависимости `get_db_session`
- фабрику FastAPI-приложения
- HTTP-клиент для интеграционных тестов
- фикстуры для performance тестов с pytest-postgresql
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import AsyncIterator

import pytest
import pytest_asyncio
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


@pytest_asyncio.fixture()
async def test_sessionmaker(test_db_url: str) -> async_sessionmaker[AsyncSession]:
    """Создает sessionmaker для тестов с SQLite."""
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(
        test_db_url,
        echo=False,
        future=True,
    )

    sessionmaker = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autoflush=False,
    )

    # Создаём таблицы
    async with engine.begin() as conn:
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)

    yield sessionmaker

    # Очистка
    async with engine.begin() as conn:
        from app.models import Base
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


@pytest_asyncio.fixture()
async def app(
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


@pytest_asyncio.fixture()
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


# === Фикстуры для performance тестов с pytest-postgresql ===


@pytest_asyncio.fixture(scope='function')
async def performance_sessionmaker(postgresql):
    """Создает sessionmaker для performance тестов с использованием pytest-postgresql."""
    if not postgresql:
        pytest.skip('PostgreSQL не доступен для performance тестов')

    # Создаем асинхронный движок для тестов
    # Создаем правильный URL для SQLAlchemy
    dsn_parts = postgresql.info.dsn.split()
    host = None
    port = None
    user = None
    password = None
    database = None

    for part in dsn_parts:
        if part.startswith('host='):
            host = part.split('=')[1]
        elif part.startswith('port='):
            port = part.split('=')[1]
        elif part.startswith('user='):
            user = part.split('=')[1]
        elif part.startswith('password='):
            password = part.split('=')[1]
        elif part.startswith('dbname='):
            database = part.split('=')[1]

    # Формируем URL для SQLAlchemy
    if password:
        database_url = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'
    else:
        database_url = f'postgresql+asyncpg://{user}@{host}:{port}/{database}'

    perf_engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        pool_size=20,  # Увеличиваем размер пула для performance тестов
        max_overflow=40,  # Увеличиваем overflow для одновременных запросов
        pool_pre_ping=True,
        pool_recycle=1800,
        isolation_level='READ_COMMITTED',
    )

    sessionmaker = async_sessionmaker(
        perf_engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autoflush=False,
    )

    yield sessionmaker

    # Очистка
    await perf_engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def performance_app(performance_sessionmaker):
    """Создает тестовое приложение для performance тестов."""
    from app.main import create_app

    # Создаем копию приложения без lifespan для тестов
    test_app = create_app()

    # Переопределяем зависимости для БД с реальными репозиториями
    async def override_get_db_session():
        async with performance_sessionmaker() as session:
            yield session

    test_app.dependency_overrides[get_db_session] = override_get_db_session

    yield test_app


@pytest_asyncio.fixture(scope='function')
async def performance_client(performance_app):
    """HTTP-клиент для performance тестов."""
    transport = ASGITransport(app=performance_app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture()
def make_performance_token(performance_app) -> callable:  # type: ignore[name-defined,type-arg]
    """Создать функцию для генерации тестовых токенов для performance тестов.

    Args:
        performance_app: Тестовое приложение с настройками.

    Returns:
        callable: Функция для создания токенов.
    """
    from app.core.security import create_access_token
    from app.core.config import get_settings

    def _make_performance_token(user_id: int) -> str:
        """Создать токен для пользователя используя настройки приложения."""
        settings = get_settings()
        return create_access_token(
            user_id,
            settings.jwt_secret,
            settings.jwt_algorithm,
            settings.jwt_expires_minutes,
        )

    return _make_performance_token


@pytest_asyncio.fixture(scope='function', autouse=True)
async def clean_database(performance_sessionmaker, setup_test_database):
    """Очищает данные между тестами для изоляции."""
    if not performance_sessionmaker:
        yield
        return

    async def cleanup():
        async with performance_sessionmaker() as session:
            from sqlalchemy import text

            # Очищаем таблицы в правильном порядке (сначала payments, потом accounts, потом users)
            await session.execute(text('DELETE FROM payments'))
            await session.execute(text('DELETE FROM accounts'))
            await session.execute(text('DELETE FROM users'))
            await session.commit()

    # Запускаем очистку перед тестом
    await cleanup()

    yield

    # Очищаем после теста тоже
    await cleanup()


# === Фикстуры для pytest-postgresql ===


@pytest.fixture(scope='function', autouse=True)
def setup_test_database(postgresql):
    """Автоматическая настройка тестовой базы данных."""
    if postgresql:
        # Создаем таблицы в тестовой БД
        from app.models import Base

        # Синхронный движок для создания таблиц
        # Создаем правильный URL для SQLAlchemy
        dsn_parts = postgresql.info.dsn.split()
        host = None
        port = None
        user = None
        password = None
        database = None

        for part in dsn_parts:
            if part.startswith('host='):
                host = part.split('=')[1]
            elif part.startswith('port='):
                port = part.split('=')[1]
            elif part.startswith('user='):
                user = part.split('=')[1]
            elif part.startswith('password='):
                password = part.split('=')[1]
            elif part.startswith('dbname='):
                database = part.split('=')[1]

        # Формируем URL для SQLAlchemy
        if password:
            sqlalchemy_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        else:
            sqlalchemy_url = f'postgresql://{user}@{host}:{port}/{database}'

        from sqlalchemy import create_engine
        sync_engine = create_engine(sqlalchemy_url, echo=False)

        # Создаем все таблицы
        Base.metadata.create_all(bind=sync_engine)

        yield

        # Очищаем таблицы после всех тестов
        Base.metadata.drop_all(bind=sync_engine)
        sync_engine.dispose()
    else:
        yield


# === Вспомогательные фикстуры для performance тестов ===


@pytest.fixture
def performance_settings():
    """Настройки для performance тестов."""
    return {
        'bulk_operations_threshold': 60.0,  # секунд
        'concurrent_operations_threshold': 30.0,  # секунд
        'query_performance_threshold': 10.0,  # секунд
        'stress_test_threshold': 60.0,  # секунд
        'memory_increase_threshold': 200,  # MB
        'success_rate_threshold': 0.8,  # 80%
    }


@pytest.fixture
def performance_metrics():
    """Метрики для performance тестов."""
    return {
        'min_users_per_second': 0.8,
        'min_queries_per_second': 10,
        'max_operation_time': 10.0,
        'max_memory_increase': 100,  # MB
    }


def pytest_configure(config):
    """Конфигурация pytest."""
    # Регистрируем кастомные маркеры
    config.addinivalue_line('markers', 'performance: marks tests as performance tests')
    config.addinivalue_line('markers', 'slow: marks tests as slow tests')
    config.addinivalue_line('markers', 'stress: marks tests as stress tests')


def pytest_collection_modifyitems(config, items):
    """Модифицирует собранные тесты."""
    for item in items:
        # Добавляем маркеры по умолчанию на основе пути к файлу
        if 'performance' in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        # Добавляем маркер slow для performance тестов
        if 'performance' in str(item.fspath):
            item.add_marker(pytest.mark.slow)
