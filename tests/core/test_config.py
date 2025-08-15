"""Тесты конфигурации Settings - все сценарии."""

from __future__ import annotations

import os

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from tests.constants import (
    TestAuthConstants,
    TestEnvData,
    TestEnvKeys,
    TestUserData,
    TestValidationData,
)


class TestSettings:
    """Тесты базовых и расширенных сценариев конфигурации."""

    def test_get_settings(self) -> None:
        """Тест получения настроек приложения."""
        settings = get_settings()
        assert settings is not None
        assert settings.app_name == TestUserData.TEST_APP_NAME
        assert settings.jwt_algorithm == TestUserData.TEST_JWT_ALGORITHM
        assert settings.jwt_expires_minutes > 0

    def test_settings_returns_settings(self) -> None:
        """get_settings возвращает валидный экземпляр Settings (без синглтона)."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert isinstance(settings1, Settings)
        assert isinstance(settings2, Settings)
        assert settings1 is not None and settings2 is not None

    def test_settings_builds_database_urls(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Построение URL для БД из компонентов окружения."""
        for key in (
            TestEnvKeys.DATABASE_URL,
            TestEnvKeys.SYNC_DATABASE_URL,
            TestEnvKeys.DB_ASYNC_DRIVER,
            TestEnvKeys.DB_SYNC_DRIVER,
            TestEnvKeys.DB_USER,
            TestEnvKeys.DB_PASSWORD,
            TestEnvKeys.DB_HOST,
            TestEnvKeys.DB_PORT,
            TestEnvKeys.DB_NAME,
            TestEnvKeys.JWT_SECRET,
            TestEnvKeys.WEBHOOK_SECRET_KEY,
        ):
            monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.DB_ASYNC_DRIVER, TestEnvData.DB_ASYNC_DRIVER)
        monkeypatch.setenv(TestEnvKeys.DB_SYNC_DRIVER, TestEnvData.DB_SYNC_DRIVER)
        monkeypatch.setenv(TestEnvKeys.DB_USER, TestEnvData.DB_USER)
        monkeypatch.setenv(TestEnvKeys.DB_PASSWORD, TestEnvData.DB_PASSWORD)
        monkeypatch.setenv(TestEnvKeys.DB_HOST, TestEnvData.DB_HOST)
        monkeypatch.setenv(TestEnvKeys.DB_PORT, TestEnvData.DB_PORT)
        monkeypatch.setenv(TestEnvKeys.DB_NAME, TestEnvData.DB_NAME)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.TEST_SECRET)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.TEST_WEBHOOK_SECRET
        )

        settings = get_settings()
        expected_async = (
            f"{TestEnvData.DB_ASYNC_DRIVER}://{TestEnvData.DB_USER}:{TestEnvData.DB_PASSWORD}"
            f"@{TestEnvData.DB_HOST}:{TestEnvData.DB_PORT}/{TestEnvData.DB_NAME}"
        )
        expected_sync = (
            f"{TestEnvData.DB_SYNC_DRIVER}://{TestEnvData.DB_USER}:{TestEnvData.DB_PASSWORD}"
            f"@{TestEnvData.DB_HOST}:{TestEnvData.DB_PORT}/{TestEnvData.DB_NAME}"
        )
        assert settings.database_url.startswith(expected_async)
        assert settings.sync_database_url.startswith(expected_sync)

    def test_settings_cors_origins_string_single(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тест CORS origins с одной строкой."""
        for key in (TestEnvKeys.DATABASE_URL, TestEnvKeys.CORS_ORIGINS):
            monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_TEST)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.TEST_WEBHOOK_SECRET
        )
        monkeypatch.setenv(TestEnvKeys.CORS_ORIGINS, TestValidationData.ORIGIN_EXAMPLE)

        settings = get_settings()
        assert settings.cors_origins == [TestValidationData.ORIGIN_EXAMPLE]

    def test_settings_cors_origins_string_multiple(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тест CORS origins с несколькими строками."""
        for key in (TestEnvKeys.DATABASE_URL, TestEnvKeys.CORS_ORIGINS):
            monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_TEST)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.TEST_WEBHOOK_SECRET
        )
        monkeypatch.setenv(
            TestEnvKeys.CORS_ORIGINS,
            f"{TestValidationData.ORIGIN_EXAMPLE},{TestValidationData.ORIGIN_TEST},{TestValidationData.ORIGIN_API}",
        )

        settings = get_settings()
        expected = [
            TestValidationData.ORIGIN_EXAMPLE,
            TestValidationData.ORIGIN_TEST,
            TestValidationData.ORIGIN_API,
        ]
        assert settings.cors_origins == expected

    def test_settings_cors_origins_wildcard(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тест CORS origins с wildcard."""
        for key in (TestEnvKeys.DATABASE_URL, TestEnvKeys.CORS_ORIGINS):
            monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_TEST)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.TEST_WEBHOOK_SECRET
        )
        monkeypatch.setenv(TestEnvKeys.CORS_ORIGINS, TestValidationData.CORS_WILDCARD)

        settings = get_settings()
        assert settings.cors_origins == [TestValidationData.CORS_WILDCARD]

    def test_settings_cors_origins_with_spaces(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тест CORS origins с пробелами."""
        for key in (TestEnvKeys.DATABASE_URL, TestEnvKeys.CORS_ORIGINS):
            monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_TEST)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.TEST_WEBHOOK_SECRET
        )
        monkeypatch.setenv(
            TestEnvKeys.CORS_ORIGINS, TestValidationData.ORIGINS_WITH_SPACES
        )

        settings = get_settings()
        assert settings.cors_origins == [
            TestValidationData.ORIGIN_EXAMPLE,
            TestValidationData.ORIGIN_TEST,
        ]

    def test_settings_cors_origins_empty_values(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тест CORS origins с пустыми значениями."""
        for key in (TestEnvKeys.DATABASE_URL, TestEnvKeys.CORS_ORIGINS):
            monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_TEST)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.TEST_WEBHOOK_SECRET
        )
        monkeypatch.setenv(
            TestEnvKeys.CORS_ORIGINS, TestValidationData.ORIGINS_WITH_EMPTY
        )

        settings = get_settings()
        assert settings.cors_origins == [
            TestValidationData.ORIGIN_EXAMPLE,
            TestValidationData.ORIGIN_TEST,
        ]

    def test_settings_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест значений по умолчанию."""
        for key in list(os.environ.keys()):
            if key.startswith(TestEnvKeys.PREFIXES):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_TEST)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.TEST_WEBHOOK_SECRET
        )
        monkeypatch.setenv(TestEnvKeys.DEBUG, TestEnvData.DEBUG_FALSE)
        monkeypatch.setenv(TestEnvKeys.ENV, TestEnvData.ENV_PRODUCTION)

        settings = get_settings()
        assert settings.app_name == TestUserData.TEST_APP_NAME
        assert settings.debug is False
        assert settings.cors_origins == [TestValidationData.CORS_WILDCARD]
        assert settings.jwt_algorithm == TestUserData.TEST_JWT_ALGORITHM
        assert (
            settings.jwt_expires_minutes
            == TestAuthConstants.JWT_EXPIRES_MINUTES_DEFAULT
        )

    def test_settings_environment_production(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тест настроек для production окружения."""
        for key in list(os.environ.keys()):
            if key.startswith(TestEnvKeys.PREFIXES):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.ENV, TestEnvData.ENV_PRODUCTION)
        monkeypatch.setenv(TestEnvKeys.DEBUG, TestEnvData.DEBUG_FALSE)
        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.POSTGRES_PROD_URL)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_PROD)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.WEBHOOK_SECRET_PROD
        )
        monkeypatch.setenv(TestEnvKeys.CORS_ORIGINS, TestValidationData.ORIGIN_API)

        settings = get_settings()
        assert settings.debug is False
        assert settings.cors_origins == [TestValidationData.ORIGIN_API]

    def test_settings_environment_development(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тест настроек для development окружения."""
        for key in list(os.environ.keys()):
            if key.startswith(TestEnvKeys.PREFIXES):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(TestEnvKeys.ENV, TestEnvData.ENV_DEVELOPMENT)
        monkeypatch.setenv(TestEnvKeys.DEBUG, TestEnvData.DEBUG_TRUE)
        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_DEV)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.WEBHOOK_SECRET_DEV
        )

        settings = get_settings()
        assert settings.debug is True

    def test_settings_missing_jwt_secret(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест отсутствующего JWT секрета."""
        for key in (
            TestEnvKeys.JWT_SECRET,
            TestEnvKeys.DATABASE_URL,
            TestEnvKeys.WEBHOOK_SECRET_KEY,
        ):
            monkeypatch.delenv(key, raising=False)

        import shutil
        from pathlib import Path

        temp_files = []
        for env_file in TestEnvData.ENV_FILES:
            if Path(env_file).exists():
                temp_name = f"{env_file}.temp_{os.getpid()}"
                shutil.move(env_file, temp_name)
                temp_files.append((env_file, temp_name))

        try:
            monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
            monkeypatch.setenv(
                TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.TEST_WEBHOOK_SECRET
            )

            with pytest.raises(ValidationError):
                Settings()
        finally:
            for original, temp in temp_files:
                shutil.move(temp, original)

    def test_settings_missing_webhook_secret(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тест отсутствующего webhook секрета."""
        for key in (
            TestEnvKeys.JWT_SECRET,
            TestEnvKeys.DATABASE_URL,
            TestEnvKeys.WEBHOOK_SECRET_KEY,
        ):
            monkeypatch.delenv(key, raising=False)

        import shutil
        from pathlib import Path

        temp_files = []
        for env_file in TestEnvData.ENV_FILES:
            if Path(env_file).exists():
                temp_name = f"{env_file}.temp_{os.getpid()}"
                shutil.move(env_file, temp_name)
                temp_files.append((env_file, temp_name))

        try:
            monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)
            monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_TEST)

            with pytest.raises(ValidationError):
                Settings()
        finally:
            for original, temp in temp_files:
                shutil.move(temp, original)

    def test_settings_no_caching(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Тест отсутствия кэширования настроек."""
        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_1)
        monkeypatch.setenv(
            TestEnvKeys.WEBHOOK_SECRET_KEY, TestUserData.WEBHOOK_SECRET_1
        )
        monkeypatch.setenv(TestEnvKeys.DATABASE_URL, TestEnvData.SQLITE_MEMORY_URL)

        settings1 = get_settings()
        assert settings1.jwt_secret == TestUserData.JWT_SECRET_1

        monkeypatch.setenv(TestEnvKeys.JWT_SECRET, TestUserData.JWT_SECRET_2)

        settings2 = get_settings()
        assert settings2.jwt_secret == TestUserData.JWT_SECRET_2
        assert settings1 is not settings2
