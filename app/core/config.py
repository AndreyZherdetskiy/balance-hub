"""Конфигурация приложения на основе pydantic-settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_env_file() -> str:
    """Определить .env файл с учётом среды выполнения.

    Приоритет выбора:
    0. ENV_FILE — явное переопределение файла (если задан)
    1. Если приложение запущено в контейнере Docker — `.env.docker`
    2. Иначе — `.env.local`
    3. Fallback — `.env`

    Returns:
        str: Путь к файлу конфигурации.
    """
    override = os.getenv('ENV_FILE')
    if override and Path(override).exists():
        return override

    running_in_docker = Path('/.dockerenv').exists() or os.getenv('DOCKER') == '1'
    if running_in_docker and Path('.env.docker').exists():
        return '.env.docker'

    if Path('.env.local').exists():
        return '.env.local'

    if Path('.env').exists():
        return '.env'

    # Если ни один файл не найден, возвращаем .env как fallback (может и не существовать)
    return '.env'


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из окружения.

    Атрибуты:
        app_name: Название приложения.
        env: Окружение (dev/prod и т.д.).
        debug: Флаг отладки.
        cors_origins: Разрешённые Origins для CORS.
        jwt_secret: Секрет для подписи JWT.
        jwt_algorithm: Алгоритм JWT (по умолчанию HS256).
        jwt_expires_minutes: Время жизни токена в минутах.
        webhook_secret_key: Секретный ключ для подписи вебхука.
        database_url: Строка подключения к БД (async, для приложения).
        sync_database_url: Строка подключения к БД (опционально для инструментов).
    """

    model_config = SettingsConfigDict(
        env_file=_get_env_file(), env_file_encoding='utf-8', extra='ignore'
    )

    app_name: str = 'BalanceHub'
    env: str = 'dev'
    debug: bool = True

    cors_origins: List[AnyHttpUrl] | List[str] = ['*']

    jwt_secret: str
    jwt_algorithm: str = 'HS256'
    jwt_expires_minutes: int = 60

    webhook_secret_key: str

    # Драйверы и компоненты подключения к БД
    db_async_driver: str = 'postgresql+asyncpg'
    db_sync_driver: str = 'postgresql+psycopg2'
    db_user: str | None = None
    db_password: str | None = None
    db_host: str | None = None
    db_port: int | None = None
    db_name: str | None = None

    # Полные URL могут быть заданы напрямую, либо будут собраны динамически из компонентов выше
    database_url: str | None = None
    sync_database_url: str | None = None

    @field_validator('cors_origins', mode='before')
    def split_cors_origins(cls, value: str | List[str]):  # type: ignore[override]
        """Преобразовать строку Origins в список.

        Args:
            value: Значение из окружения.

        Returns:
            list[str] | list[AnyHttpUrl]: Нормализованный список Origins.
        """
        if isinstance(value, str):
            if value == '*':
                return ['*']
            return [v.strip() for v in value.split(',') if v.strip()]
        return value

    @field_validator('database_url', mode='before')
    def build_async_url(cls, v, info):  # type: ignore[override]
        """Собрать DATABASE_URL, если не задан напрямую.

        Args:
            v: Значение из окружения.
            info: Информация о конфигурации.

        Returns:
            str: Собранный URL.
        """
        if v:
            return v
        data = info.data
        parts = (
            data.get('db_async_driver'),
            data.get('db_user'),
            data.get('db_password'),
            data.get('db_host'),
            data.get('db_port'),
            data.get('db_name'),
        )
        if all(parts):
            return f'{data["db_async_driver"]}://{data["db_user"]}:{data["db_password"]}@{data["db_host"]}:{data["db_port"]}/{data["db_name"]}'
        return v

    @field_validator('sync_database_url', mode='before')
    def build_sync_url(cls, v, info):  # type: ignore[override]
        """Собрать SYNC_DATABASE_URL, если не задан напрямую.

        Args:
            v: Значение из окружения.
            info: Информация о конфигурации.

        Returns:
            str: Собранный URL.
        """
        if v:
            return v
        data = info.data
        parts = (
            data.get('db_sync_driver'),
            data.get('db_user'),
            data.get('db_password'),
            data.get('db_host'),
            data.get('db_port'),
            data.get('db_name'),
        )
        if all(parts):
            return f'{data["db_sync_driver"]}://{data["db_user"]}:{data["db_password"]}@{data["db_host"]}:{data["db_port"]}/{data["db_name"]}'
        return v


def get_settings() -> Settings:
    """Получить актуальный экземпляр настроек.

    Не кэширует критические настройки безопасности (JWT_SECRET, WEBHOOK_SECRET_KEY)
    для предотвращения проблем с обновлением настроек в тестах и деплое.

    Returns:
        Settings: Настройки приложения.
    """
    settings = Settings()  # type: ignore[call-arg]
    # Последняя валидация: убеждаемся, что URLы сформированы
    if not settings.database_url:
        raise ValueError('DATABASE_URL не задан и не может быть собран из компонентов подключения')
    if not settings.sync_database_url:
        # Не критично для работы приложения, но полезно для инструментов
        settings.sync_database_url = settings.database_url.replace(
            settings.db_async_driver, settings.db_sync_driver
        )
    return settings
