"""Pydantic-схемы для пользователя."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants.field_constraints import FieldConstraints
from app.core.constants.regex import RegexPatterns


class BaseEmailFieldMixin(BaseModel):
    """Базовый миксин для опционального поля email с валидацией."""

    email: EmailStr | None = Field(
        default=None,
        min_length=FieldConstraints.USER_EMAIL_MIN_LENGTH,
        max_length=FieldConstraints.USER_EMAIL_MAX_LENGTH,
    )


class BasePasswordFieldMixin(BaseModel):
    """Базовый миксин для опционального поля password с валидацией."""

    password: str | None = Field(
        default=None,
        min_length=FieldConstraints.PASSWORD_MIN_LENGTH,
        max_length=FieldConstraints.PASSWORD_MAX_LENGTH,
    )


class BaseFullNameFieldMixin(BaseModel):
    """Базовый миксин для опционального поля full_name с валидацией."""

    full_name: str | None = Field(
        default=None,
        min_length=FieldConstraints.USER_FULL_NAME_MIN_LENGTH,
        max_length=FieldConstraints.USER_FULL_NAME_MAX_LENGTH,
        pattern=RegexPatterns.FULL_NAME,
    )


class EmailFieldMixin(BaseEmailFieldMixin):
    """Миксин для обязательного поля email с валидацией."""

    email: EmailStr = Field(
        min_length=FieldConstraints.USER_EMAIL_MIN_LENGTH,
        max_length=FieldConstraints.USER_EMAIL_MAX_LENGTH,
    )


class PasswordFieldMixin(BasePasswordFieldMixin):
    """Миксин для обязательного поля password с валидацией."""

    password: str = Field(
        min_length=FieldConstraints.PASSWORD_MIN_LENGTH,
        max_length=FieldConstraints.PASSWORD_MAX_LENGTH,
    )


class FullNameFieldMixin(BaseFullNameFieldMixin):
    """Миксин для обязательного поля full_name с валидацией."""

    full_name: str = Field(
        min_length=FieldConstraints.USER_FULL_NAME_MIN_LENGTH,
        max_length=FieldConstraints.USER_FULL_NAME_MAX_LENGTH,
        pattern=RegexPatterns.FULL_NAME,
    )


class UserBase(EmailFieldMixin, FullNameFieldMixin):
    """Базовые поля пользователя."""


class UserCreate(UserBase, PasswordFieldMixin):
    """Схема создания пользователя (админ)."""

    is_admin: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "john@example.com",
                    "full_name": "John Doe",
                    "password": "StrongPassw0rd!",
                    "is_admin": False,
                }
            ]
        }
    )


class UserUpdate(BaseEmailFieldMixin, BaseFullNameFieldMixin, BasePasswordFieldMixin):
    """Схема обновления пользователя (админ)."""

    is_admin: bool | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"email": "newmail@example.com", "full_name": "New Name"}]
        }
    )


class UserPublic(UserBase):
    """Публичное представление пользователя."""

    id: int
    is_admin: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "email": "user@example.com",
                    "full_name": "Test User",
                    "is_admin": False,
                }
            ]
        },
    )


class Token(BaseModel):
    """Ответ с JWT токеном."""

    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"access_token": "eyJhbGciOi...signature", "token_type": "bearer"}
            ]
        }
    )


class LoginRequest(EmailFieldMixin, PasswordFieldMixin):
    """Запрос на вход."""

    pass

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"email": "user@example.com", "password": "Password123!"}]
        }
    )
