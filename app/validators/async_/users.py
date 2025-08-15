from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages
from app.core.errors import NotFoundError, ValidationError
from app.crud.users import CRUDUser
from app.models.user import User


class UserAsyncValidator:
    """Асинхронные проверки инвариантов пользователя.

    Использует CRUD-уровень для запросов к БД. Бросает доменные ошибки.
    """

    def __init__(self, users_crud: CRUDUser) -> None:
        """Инициализирует валидатор пользователей.

        Args:
            users_crud: CRUD-уровень для работы с пользователями.
        """
        self.users_crud = users_crud

    async def assert_email_unique(
        self, db: AsyncSession, email: str, *, exclude_user_id: Optional[int] = None
    ) -> None:
        """Проверяет, что email не занят другим пользователем.

        Args:
            db (AsyncSession): Сессия БД.
            email (str): Проверяемый email.
            exclude_user_id (Optional[int]): Исключить пользователя с этим ID из проверки (для update).

        Raises:
            ValidationError: Если email уже используется другим пользователем.
        """
        existing = await self.users_crud.get_by_email(db, email)
        if existing is None:
            return
        if exclude_user_id is not None and existing.id == exclude_user_id:
            return
        raise ValidationError(ErrorMessages.EMAIL_ALREADY_EXISTS)

    async def get_user_or_error(self, db: AsyncSession, user_id: int) -> User:
        """Возвращает пользователя или бросает `NotFoundError`.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.

        Returns:
            User: Найденный пользователь.

        Raises:
            NotFoundError: Если пользователь не найден.
        """
        user = await self.users_crud.get(db, user_id)
        if user is None:
            raise NotFoundError(ErrorMessages.USER_NOT_FOUND)
        return user
