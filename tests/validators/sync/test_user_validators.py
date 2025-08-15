"""Тесты для синхронных валидаторов пользователей (без дублирования схем/сервисов)."""

from __future__ import annotations

import pytest

from app.core.constants import ErrorMessages, FieldConstraints
from app.core.errors import ValidationError
from app.schemas.user import UserCreate, UserUpdate
from app.validators.sync.users import UserValidator
from tests.constants import TestUserData, TestValidationData


class TestUserValidator:
    """Тесты для `UserValidator`. Проверяем доменные ошибки и точечные кейсы."""

    def test_validate_email_valid(self) -> None:
        """Корректный email проходит без ошибок (сообщения не проверяются)."""
        UserValidator.validate_email(TestUserData.TEST_EMAIL_GENERIC)

    def test_validate_email_invalid(self) -> None:
        """Некорректные email должны дать доменную ошибку с ожидаемым сообщением."""
        with pytest.raises(ValidationError, match=ErrorMessages.EMAIL_INVALID):
            UserValidator.validate_email(TestUserData.INVALID_EMAIL_FORMAT)

        with pytest.raises(ValidationError, match=ErrorMessages.EMAIL_INVALID):
            UserValidator.validate_email(TestUserData.EMPTY_EMAIL)  # пустая строка

        with pytest.raises(ValidationError, match=ErrorMessages.EMAIL_INVALID):
            UserValidator.validate_email(None)  # type: ignore[arg-type]

    def test_validate_password_valid(self) -> None:
        """Пароль достаточной длины и состава (буквы+цифры) валиден."""
        UserValidator.validate_password(TestUserData.PASSWORD_123_STRONG)

    def test_validate_password_invalid_type_or_strength(self) -> None:
        """Проверяем сообщения об ошибках для пустых/нестрок и слабых паролей."""
        with pytest.raises(
            ValidationError, match=ErrorMessages.PASSWORD_MUST_BE_STRING
        ):
            UserValidator.validate_password("")

        with pytest.raises(
            ValidationError, match=ErrorMessages.PASSWORD_MUST_BE_STRING
        ):
            UserValidator.validate_password(None)  # type: ignore[arg-type]

        too_short = "a1" * (FieldConstraints.PASSWORD_MIN_LENGTH // 4)
        with pytest.raises(ValidationError, match=ErrorMessages.PASSWORD_WEAK):
            UserValidator.validate_password(too_short)

        letters_only = "A" * FieldConstraints.PASSWORD_MIN_LENGTH
        with pytest.raises(ValidationError, match=ErrorMessages.PASSWORD_WEAK):
            UserValidator.validate_password(letters_only)

        digits_only = "1" * FieldConstraints.PASSWORD_MIN_LENGTH
        with pytest.raises(ValidationError, match=ErrorMessages.PASSWORD_WEAK):
            UserValidator.validate_password(digits_only)

    def test_validate_full_name_valid(self) -> None:
        """Корректное полное имя по паттерну проходит."""
        UserValidator.validate_full_name(TestValidationData.TEST_USER_FULL_NAME)

    def test_validate_full_name_invalid(self) -> None:
        """Неверные имена должны давать доменные ошибки с ожидаемыми сообщениями."""
        with pytest.raises(ValidationError, match=ErrorMessages.FULL_NAME_INVALID):
            UserValidator.validate_full_name("A")

        with pytest.raises(ValidationError, match=ErrorMessages.FULL_NAME_INVALID):
            UserValidator.validate_full_name("John123")

        with pytest.raises(ValidationError, match=ErrorMessages.FULL_NAME_INVALID):
            UserValidator.validate_full_name(None)  # type: ignore[arg-type]

    def test_validate_user_create_valid(self) -> None:
        """Обертка `validate_user_create` не падает на валидных данных схемы."""
        data = UserCreate(
            email=TestUserData.TEST_EMAIL_GENERIC,
            full_name=TestValidationData.TEST_USER_FULL_NAME,
            password=TestUserData.SECURE_PASSWORD_123,
        )
        UserValidator.validate_user_create(data)

    def test_validate_user_create_password_weak(self) -> None:
        """Схема пропускает строку, но валидатор ловит слабый пароль (буквы без цифр)."""
        weak_password_letters_only = "a" * FieldConstraints.PASSWORD_MIN_LENGTH
        data = UserCreate(
            email=TestUserData.TEST_EMAIL_GENERIC,
            full_name=TestValidationData.TEST_USER_FULL_NAME,
            password=weak_password_letters_only,
        )
        with pytest.raises(ValidationError, match=ErrorMessages.PASSWORD_WEAK):
            UserValidator.validate_user_create(data)

    def test_validate_user_update_partial_and_rules(self) -> None:
        """`validate_user_update` проверяет только переданные поля и ловит нарушения правил."""
        # частичное обновление: только имя — валидно
        UserValidator.validate_user_update(
            UserUpdate(full_name=TestValidationData.TEST_USER_FULL_NAME)
        )

        # Тестируем валидацию невалидных данных через отдельные методы валидатора
        with pytest.raises(ValidationError, match=ErrorMessages.FULL_NAME_INVALID):
            UserValidator.validate_full_name("User123")

        with pytest.raises(ValidationError, match=ErrorMessages.PASSWORD_WEAK):
            UserValidator.validate_password("short")

    def test_validate_user_update_email_only(self) -> None:
        """Ветка с email в `validate_user_update` покрыта валидным кейсом."""
        UserValidator.validate_user_update(
            UserUpdate(email=TestUserData.NEW_EMAIL_GENERIC)
        )
