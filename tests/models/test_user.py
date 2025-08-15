"""Тесты для модели User - все сценарии."""

from __future__ import annotations

from app.models.user import User
from tests.constants import TestUserData, TestValidationData


class TestUserModel:
    """Тесты модели User."""

    def test_user_model_creation(self) -> None:
        """Тест создания модели пользователя."""
        user = User(
            email=TestUserData.TEST_EMAIL_GENERIC,
            full_name=TestValidationData.TEST_USER_FULL_NAME,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
            is_admin=False,
        )

        assert user.email == TestUserData.TEST_EMAIL_GENERIC
        assert user.full_name == TestValidationData.TEST_USER_FULL_NAME
        assert user.hashed_password == TestUserData.TEST_HASHED_PASSWORD
        assert user.is_admin is False

    def test_user_model_defaults(self) -> None:
        """Тест модели пользователя с значениями по умолчанию."""
        user = User(
            email=TestUserData.TEST_EMAIL_GENERIC,
            full_name=TestValidationData.TEST_USER_FULL_NAME,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
        )

        # По умолчанию значение задаётся ORM при INSERT
        assert user.is_admin is None or user.is_admin is False

    def test_user_model_admin(self) -> None:
        """Тест модели пользователя-администратора."""
        admin = User(
            email=TestUserData.ADMIN_EMAIL,
            full_name=TestUserData.ADMIN_FULL_NAME,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
            is_admin=True,
        )

        assert admin.is_admin is True

    def test_user_model_long_email(self) -> None:
        """Тест модели пользователя с длинным email."""
        long_email = TestUserData.LONG_EMAIL_MAX_LOCAL_EXAMPLE
        user = User(
            email=long_email,
            full_name=TestValidationData.TEST_USER_FULL_NAME,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
        )

        assert user.email == long_email

    def test_user_model_long_name(self) -> None:
        """Тест модели пользователя с длинным именем."""
        long_name = TestUserData.LONG_NAME_1000_A
        user = User(
            email=TestUserData.TEST_EMAIL_GENERIC,
            full_name=long_name,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
        )

        assert user.full_name == long_name

    def test_user_model_unicode_data(self) -> None:
        """Тест модели пользователя с Unicode данными."""
        user = User(
            email=TestUserData.USER_EMAIL_UNICODE_RU,
            full_name=TestUserData.FULL_NAME_UNICODE_MIXED,
            hashed_password=TestUserData.HASHED_PASSWORD_UNICODE,
        )

        assert user.email == TestUserData.USER_EMAIL_UNICODE_RU
        assert user.full_name == TestUserData.FULL_NAME_UNICODE_MIXED
        assert user.hashed_password == TestUserData.HASHED_PASSWORD_UNICODE

    def test_user_model_special_chars(self) -> None:
        """Тест модели пользователя со специальными символами."""
        user = User(
            email=TestUserData.EMAIL_WITH_TAG,
            full_name=TestUserData.FULL_NAME_WITH_PUNCT,
            hashed_password=TestUserData.HASHED_PASSWORD_WITH_SPECIALS,
            is_admin=True,
        )

        assert user.email == TestUserData.EMAIL_WITH_TAG
        assert user.full_name == TestUserData.FULL_NAME_WITH_PUNCT
        assert user.hashed_password == TestUserData.HASHED_PASSWORD_WITH_SPECIALS
        assert user.is_admin is True

    def test_user_model_empty_strings(self) -> None:
        """Тест модели пользователя с пустыми строками."""
        user = User(
            email=TestUserData.EMPTY_EMAIL,
            full_name=TestValidationData.EMPTY_STRING,
            hashed_password=TestValidationData.EMPTY_STRING,
            is_admin=False,
        )

        assert user.email == TestUserData.EMPTY_EMAIL
        assert user.full_name == TestValidationData.EMPTY_STRING
        assert user.hashed_password == TestValidationData.EMPTY_STRING
