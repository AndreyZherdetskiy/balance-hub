"""Тесты для Pydantic схем пользователя - все сценарии."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.user import LoginRequest, Token, UserCreate, UserPublic, UserUpdate
from tests.constants import (
    TestAuthData,
    TestDomainConstraints,
    TestDomainIds,
    TestNumericConstants,
    TestUserData,
    TestValidationData,
)


class TestUserCreate:
    """Тесты для схемы создания пользователя."""

    def test_schema_valid(self) -> None:
        """Тест валидной схемы создания пользователя."""
        data = {
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "password": TestUserData.SECURE_PASSWORD_123,
            "is_admin": False,
        }

        user_create = UserCreate(**data)
        assert user_create.email == TestUserData.TEST_EMAIL_GENERIC
        assert user_create.full_name == TestValidationData.TEST_USER_FULL_NAME
        assert user_create.password == TestUserData.SECURE_PASSWORD_123
        assert user_create.is_admin is False

    def test_default_admin(self) -> None:
        """Тест значения по умолчанию для is_admin."""
        data = {
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "password": TestUserData.SECURE_PASSWORD_123,
        }

        user_create = UserCreate(**data)
        assert user_create.is_admin is False

    def test_short_password(self) -> None:
        """Тест валидации короткого пароля."""
        data = {
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "password": TestUserData.SHORT_PASSWORD,
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        errors = exc_info.value.errors()
        assert any("at least 8 characters" in str(error["msg"]) for error in errors)

    def test_invalid_email(self) -> None:
        """Тест валидации некорректного email."""
        data = {
            "email": TestUserData.INVALID_EMAIL_FORMAT,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "password": TestUserData.SECURE_PASSWORD_123,
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        errors = exc_info.value.errors()
        assert any(
            "value_error" in str(error["type"]) or "email" in str(error["type"]).lower()
            for error in errors
        )

    def test_very_long_email(self) -> None:
        """Тест валидации очень длинного email."""
        long_email = TestUserData.LONG_EMAIL_LOCAL_A200_EXAMPLE_COM
        data = {
            "email": long_email,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "password": TestUserData.SECURE_PASSWORD_123,
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        errors = exc_info.value.errors()
        assert any("too long" in str(error["msg"]) for error in errors)

    def test_very_long_name(self) -> None:
        """Тест с очень длинным именем."""
        long_name = TestUserData.LONG_NAME_500_A
        data = {
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": long_name,
            "password": TestUserData.SECURE_PASSWORD_123,
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_unicode_data(self) -> None:
        """Тест с Unicode данными."""
        data = {
            "email": TestUserData.USER_EMAIL_UNICODE_RU,
            "full_name": TestUserData.FULL_NAME_UNICODE_RU,
            "password": TestUserData.UNICODE_PASSWORD,
        }

        user_create = UserCreate(**data)
        assert user_create.email == TestUserData.USER_EMAIL_UNICODE_RU
        assert user_create.full_name == TestUserData.FULL_NAME_UNICODE_RU
        assert user_create.password == TestUserData.UNICODE_PASSWORD

    def test_special_chars_in_password(self) -> None:
        """Тест со специальными символами в пароле."""
        special_password = TestUserData.SPECIAL_PASSWORD_CHARS
        data = {
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "password": special_password,
        }

        user_create = UserCreate(**data)
        assert user_create.password == special_password

    def test_whitespace_in_name(self) -> None:
        """Тест с пробелами в имени."""
        data = {
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestUserData.FULL_NAME_WITH_SPACES,
            "password": TestUserData.SECURE_PASSWORD_123,
        }

        user_create = UserCreate(**data)
        assert user_create.full_name == TestUserData.FULL_NAME_WITH_SPACES

    def test_none_values(self) -> None:
        """Тест с None значениями."""
        data = {"email": None, "full_name": None, "password": None}

        with pytest.raises(ValidationError):
            UserCreate(**data)


class TestLoginRequest:
    """Тесты для схемы запроса входа."""

    def test_schema_valid(self) -> None:
        """Тест валидной схемы запроса входа."""
        data = {
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "password": TestUserData.PASSWORD_SIMPLE,
        }

        login_request = LoginRequest(**data)
        assert login_request.email == TestUserData.TEST_EMAIL_GENERIC
        assert login_request.password == TestUserData.PASSWORD_SIMPLE

    def test_invalid_email(self) -> None:
        """Тест невалидного email в LoginRequest."""
        data = {
            "email": TestUserData.INVALID_EMAIL_FORMAT,
            "password": TestUserData.PASSWORD_SIMPLE,
        }

        with pytest.raises(ValidationError):
            LoginRequest(**data)

    def test_missing_fields(self) -> None:
        """Тест отсутствующих полей в LoginRequest."""
        with pytest.raises(ValidationError):
            LoginRequest(password="password123")  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com")  # type: ignore[call-arg]

    def test_whitespace_in_email(self) -> None:
        """Тест с пробелами в email."""
        data = {
            "email": TestUserData.EMAIL_WITH_SPACES,
            "password": TestUserData.PASSWORD_SIMPLE,
        }

        login_request = LoginRequest(**data)
        assert login_request.email.strip() == TestUserData.TEST_EMAIL_GENERIC


class TestToken:
    """Тесты для схемы токена."""

    def test_schema(self) -> None:
        """Тест схемы токена."""
        data = {"access_token": TestUserData.JWT_TOKEN_EXAMPLE}

        token = Token(**data)
        assert token.access_token == TestUserData.JWT_TOKEN_EXAMPLE
        assert token.token_type == TestAuthData.TOKEN_TYPE

    def test_custom_type(self) -> None:
        """Тест схемы токена с кастомным типом."""
        data = {
            "access_token": TestUserData.JWT_TOKEN_EXAMPLE,
            "token_type": TestUserData.TOKEN_TYPE_CUSTOM,
        }

        token = Token(**data)
        assert token.access_token == TestUserData.JWT_TOKEN_EXAMPLE
        assert token.token_type == TestUserData.TOKEN_TYPE_CUSTOM

    def test_empty_token(self) -> None:
        """Тест схемы с пустым токеном."""
        data = {"access_token": ""}

        token = Token(**data)
        assert token.access_token == ""
        assert token.token_type == TestAuthData.TOKEN_TYPE


class TestUserUpdate:
    """Тесты для схемы обновления пользователя."""

    def test_partial(self) -> None:
        """Тест частичного обновления пользователя."""
        data = {"full_name": TestUserData.NEW_NAME}

        user_update = UserUpdate(**data)
        assert user_update.full_name == TestUserData.NEW_NAME
        assert user_update.email is None
        assert user_update.password is None
        assert user_update.is_admin is None

    def test_all_fields(self) -> None:
        """Тест обновления всех полей."""
        data = {
            "email": TestUserData.NEW_EMAIL_GENERIC,
            "full_name": TestUserData.NEW_NAME,
            "password": TestUserData.TEST_PASSWORD_NEW,
            "is_admin": True,
        }

        user_update = UserUpdate(**data)
        assert user_update.email == TestUserData.NEW_EMAIL_GENERIC
        assert user_update.full_name == TestUserData.NEW_NAME
        assert user_update.password == TestUserData.TEST_PASSWORD_NEW
        assert user_update.is_admin is True

    def test_empty(self) -> None:
        """Тест пустого обновления."""
        user_update = UserUpdate()
        assert user_update.email is None
        assert user_update.full_name is None
        assert user_update.password is None
        assert user_update.is_admin is None

    def test_invalid_email(self) -> None:
        """Тест невалидного email в обновлении."""
        data = {"email": TestUserData.INVALID_EMAIL_FORMAT}

        with pytest.raises(ValidationError):
            UserUpdate(**data)

    def test_short_password(self) -> None:
        """Тест короткого пароля в обновлении (должен проходить, валидация в CRUD)."""
        data = {"password": TestUserData.SHORT_PASSWORD}

        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**data)

        errors = exc_info.value.errors()
        assert any("at least 8 characters" in str(error["msg"]) for error in errors)

    def test_explicit_none(self) -> None:
        """Тест с явными None значениями в UserUpdate."""
        data = {"email": None, "full_name": None, "password": None, "is_admin": None}

        user_update = UserUpdate(**data)
        assert user_update.email is None
        assert user_update.full_name is None
        assert user_update.password is None
        assert user_update.is_admin is None


class TestUserPublic:
    """Тесты для публичной схемы пользователя."""

    def test_schema(self) -> None:
        """Тест публичной схемы пользователя."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "is_admin": False,
        }

        user_public = UserPublic(**data)
        assert user_public.id == TestDomainIds.TEST_USER_ID
        assert user_public.email == TestUserData.TEST_EMAIL_GENERIC
        assert user_public.full_name == TestValidationData.TEST_USER_FULL_NAME
        assert user_public.is_admin is False

    def test_with_admin(self) -> None:
        """Тест публичной схемы с полем is_admin."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "email": TestUserData.ADMIN_EMAIL,
            "full_name": TestUserData.ADMIN_USER_PUBLIC_NAME,
            "is_admin": True,
        }

        user_public = UserPublic(**data)
        assert user_public.id == TestDomainIds.TEST_USER_ID
        assert user_public.email == TestUserData.ADMIN_EMAIL
        assert user_public.full_name == TestUserData.ADMIN_USER_PUBLIC_NAME
        assert user_public.is_admin is True

    def test_missing_required_fields(self) -> None:
        """Тест отсутствующих обязательных полей в UserPublic."""
        with pytest.raises(ValidationError):
            UserPublic(
                email=TestUserData.TEST_EMAIL_GENERIC,
                full_name=TestValidationData.TEST_FULL_NAME,
            )  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            UserPublic(
                id=TestDomainIds.TEST_USER_ID,
                full_name=TestValidationData.TEST_FULL_NAME,
            )  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            UserPublic(
                id=TestDomainIds.TEST_USER_ID,
                email=TestUserData.TEST_EMAIL_GENERIC,
            )  # type: ignore[call-arg]

    def test_negative_id(self) -> None:
        """Тест с отрицательным ID."""
        data = {
            "id": TestNumericConstants.NEGATIVE_ONE,
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "is_admin": False,
        }

        user_public = UserPublic(**data)
        assert user_public.id == TestNumericConstants.NEGATIVE_ONE

    def test_zero_id(self) -> None:
        """Тест с нулевым ID."""
        data = {
            "id": TestNumericConstants.COUNT_EMPTY,
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "is_admin": False,
        }

        user_public = UserPublic(**data)
        assert user_public.id == TestNumericConstants.COUNT_EMPTY

    def test_very_large_id(self) -> None:
        """Тест с очень большим ID."""
        data = {
            "id": TestDomainConstraints.MAX_INT64,
            "email": TestUserData.TEST_EMAIL_GENERIC,
            "full_name": TestValidationData.TEST_USER_FULL_NAME,
            "is_admin": False,
        }

        user_public = UserPublic(**data)
        assert user_public.id == TestDomainConstraints.MAX_INT64


class TestUserMe:
    """Тесты для схемы текущего пользователя."""

    def test_schema(self) -> None:
        """Тест схемы текущего пользователя."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "email": TestUserData.ME_USER_EMAIL,
            "full_name": TestUserData.ME_USER_FULL_NAME,
            "is_admin": False,
        }

        user_me = UserPublic(**data)
        assert user_me.id == TestDomainIds.TEST_USER_ID
        assert user_me.email == TestUserData.ME_USER_EMAIL
        assert user_me.full_name == TestUserData.ME_USER_FULL_NAME
        assert user_me.is_admin is False

    def test_with_is_admin(self) -> None:
        """Тест схемы UserMe с полем is_admin."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "email": TestUserData.ME_USER_EMAIL,
            "full_name": TestUserData.ME_USER_FULL_NAME,
            "is_admin": True,
        }

        user_me = UserPublic(**data)
        assert user_me.id == TestDomainIds.TEST_USER_ID
        assert user_me.email == TestUserData.ME_USER_EMAIL
        assert user_me.full_name == TestUserData.ME_USER_FULL_NAME
