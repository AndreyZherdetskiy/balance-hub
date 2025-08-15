"""Бизнес-логика для работы с пользователями."""

from __future__ import annotations

from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages, PaginationParams
from app.core.errors import NotFoundError, ValidationError
from app.crud.users import CRUDUser
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.validators.async_ import UserAsyncValidator


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(
        self, users_crud: CRUDUser, user_validator: UserAsyncValidator | None = None
    ):
        """Инициализирует сервис.

        Args:
            users_crud: CRUD для пользователей.
        """
        self.users_crud = users_crud
        self.user_validator = user_validator or UserAsyncValidator(users_crud)

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Создаёт нового пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user_data (UserCreate): Данные пользователя.

        Returns:
            User: Созданный пользователь.

        Raises:
            ValidationError: Если email уже используется.
        """
        # Асинхронные инварианты
        await self.user_validator.assert_email_unique(db, user_data.email)

        try:
            user = await self.users_crud.create(
                db,
                email=user_data.email,
                full_name=user_data.full_name,
                password=user_data.password,
                is_admin=user_data.is_admin,
            )
            await db.commit()
        except IntegrityError:
            # Дублируем инвариант на случай гонок: уникальный индекс на email
            await db.rollback()
            raise ValidationError(ErrorMessages.EMAIL_ALREADY_EXISTS)

        await db.refresh(user)
        return user

    async def get_all_users(
        self,
        db: AsyncSession,
        limit: int = PaginationParams.DEFAULT_LIMIT,
        offset: int = PaginationParams.DEFAULT_OFFSET,
    ) -> List[User]:
        """Возвращает список всех пользователей.

        Args:
            db (AsyncSession): Сессия БД.
            limit (int): Максимум записей.
            offset (int): Смещение.

        Returns:
            list[User]: Список пользователей.
        """
        users = await self.users_crud.list_all_paginated(db, limit=limit, offset=offset)
        return list(users)

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User:
        """Возвращает пользователя по идентификатору.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.

        Returns:
            User: Пользователь.

        Raises:
            NotFoundError: Если пользователь не найден.
        """
        user = await self.user_validator.get_user_or_error(db, user_id)
        return user

    async def update_user(
        self, db: AsyncSession, user_id: int, user_data: UserUpdate
    ) -> User:
        """Обновляет данные существующего пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.
            user_data (UserUpdate): Поля для обновления.

        Returns:
            User: Обновлённый пользователь.

        Raises:
            NotFoundError: Если пользователь не найден.
            ValidationError: Если новый email уже используется.
        """
        user = await self.users_crud.get(db, user_id)
        if not user:
            raise NotFoundError(ErrorMessages.USER_NOT_FOUND)

        # Если обновляем email — проверить уникальность с исключением текущего пользователя
        if user_data.email is not None:
            await self.user_validator.assert_email_unique(
                db, user_data.email, exclude_user_id=user_id
            )

        user = await self.users_crud.update(
            db,
            user,
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password,
            is_admin=user_data.is_admin,
        )
        await db.commit()
        await db.refresh(user)
        return user

    async def delete_user(self, db: AsyncSession, user_id: int) -> None:
        """Удаляет пользователя по идентификатору.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.

        Raises:
            NotFoundError: Если пользователь не найден.
        """
        user = await self.user_validator.get_user_or_error(db, user_id)
        await self.users_crud.delete(db, user)
        await db.commit()
