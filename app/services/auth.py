"""Бизнес-логика для аутентификации пользователей."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import ErrorMessages
from app.core.errors import AuthError
from app.core.security import create_access_token, verify_password
from app.crud.users import CRUDUser
from app.schemas import LoginRequest


class AuthService:
    """Сервис для аутентификации пользователей."""

    def __init__(self, users_crud: CRUDUser):
        """Инициализирует сервис.

        Args:
            users_crud: CRUD для пользователей.
        """
        self.users_crud = users_crud

    async def authenticate_user(self, db: AsyncSession, login_data: LoginRequest) -> str:
        """Аутентифицирует пользователя и возвращает JWT-токен.

        Args:
            db (AsyncSession): Сессия БД.
            login_data (LoginRequest): Данные для входа (email и пароль).

        Returns:
            str: Подписанный JWT-токен.

        Raises:
            AuthError: Если пара логин/пароль неверна.
        """
        user = await self.users_crud.get_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise AuthError(ErrorMessages.INVALID_CREDENTIALS)

        settings = get_settings()
        token = create_access_token(
            user.id,
            settings.jwt_secret,
            settings.jwt_algorithm,
            settings.jwt_expires_minutes,
        )
        return token
