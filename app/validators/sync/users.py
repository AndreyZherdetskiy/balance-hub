from __future__ import annotations

import re

from app.core.constants import ErrorMessages, FieldConstraints, RegexPatterns
from app.core.errors import ValidationError
from app.schemas import UserCreate, UserUpdate


class UserValidator:
    """Валидатор данных пользователей."""

    @staticmethod
    def validate_email(email: str) -> None:
        """Проверяет корректность email адреса.

        Args:
            email (str): Email адрес для проверки.

        Raises:
            ValidationError: Если email некорректен.
        """
        if not email or not isinstance(email, str):
            raise ValidationError(ErrorMessages.EMAIL_INVALID)

        if not re.match(RegexPatterns.EMAIL, email):
            raise ValidationError(ErrorMessages.EMAIL_INVALID)

    @staticmethod
    def validate_password(password: str) -> None:
        """Проверяет сложность пароля.

        Args:
            password (str): Пароль для проверки.

        Raises:
            ValidationError: Если пароль некорректен.
        """
        if not password or not isinstance(password, str):
            raise ValidationError(ErrorMessages.PASSWORD_MUST_BE_STRING)

        if len(password) < FieldConstraints.PASSWORD_MIN_LENGTH:
            raise ValidationError(ErrorMessages.PASSWORD_WEAK)

        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_letter and has_digit):
            raise ValidationError(ErrorMessages.PASSWORD_WEAK)

    @staticmethod
    def validate_full_name(full_name: str) -> None:
        """Проверяет корректность полного имени.

        Args:
            full_name (str): Полное имя для проверки.

        Raises:
            ValidationError: Если имя некорректно.
        """
        if not full_name or not isinstance(full_name, str):
            raise ValidationError(ErrorMessages.FULL_NAME_INVALID)

        if (
            len(full_name.strip()) < FieldConstraints.USER_FULL_NAME_MIN_LENGTH
            or len(full_name) > FieldConstraints.USER_FULL_NAME_MAX_LENGTH
        ):
            raise ValidationError(ErrorMessages.FULL_NAME_INVALID)

        if not re.match(RegexPatterns.FULL_NAME, full_name):
            raise ValidationError(ErrorMessages.FULL_NAME_INVALID)

    @staticmethod
    def validate_user_create(user_data: UserCreate) -> None:
        """Проверяет данные для создания пользователя.

        Args:
            user_data (UserCreate): Данные пользователя.

        Returns:
            None
        """
        UserValidator.validate_email(user_data.email)
        UserValidator.validate_password(user_data.password)
        UserValidator.validate_full_name(user_data.full_name)

    @staticmethod
    def validate_user_update(user_data: UserUpdate) -> None:
        """Проверяет данные для обновления пользователя.

        Args:
            user_data (UserUpdate): Данные пользователя.

        Returns:
            None
        """
        if user_data.email is not None:
            UserValidator.validate_email(user_data.email)
        if user_data.password is not None:
            UserValidator.validate_password(user_data.password)
        if user_data.full_name is not None:
            UserValidator.validate_full_name(user_data.full_name)
