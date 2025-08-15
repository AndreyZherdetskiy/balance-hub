"""CRUD-операции для пользователей."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud.base import CRUDBase
from app.models.user import User


class CRUDUser(CRUDBase[User]):
    """CRUD-класс для модели `User`."""

    def __init__(self) -> None:
        """Инициализирует CRUD-класс для модели `User`.

        Args:
            model (type[User]): Класс ORM-модели.
        """
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Возвращает пользователя по email.

        Args:
            db (AsyncSession): Сессия БД.
            email (str): Email пользователя.

        Returns:
            User | None: Пользователь или None.
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        *,
        email: str,
        full_name: str,
        password: str,
        is_admin: bool = False,
    ) -> User:
        """Создаёт пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            email (str): Email.
            full_name (str): Полное имя.
            password (str): Пароль.
            is_admin (bool): Признак администратора.

        Returns:
            User: Созданный пользователь.
        """
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            is_admin=is_admin,
        )
        db.add(user)
        await db.flush()
        return user

    async def update(
        self,
        db: AsyncSession,
        user: User,
        *,
        email: str | None = None,
        full_name: str | None = None,
        password: str | None = None,
        is_admin: bool | None = None,
    ) -> User:
        """Обновляет пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user (User): Пользователь к обновлению.
            email (str | None): Новый email.
            full_name (str | None): Новое имя.
            password (str | None): Новый пароль.
            is_admin (bool | None): Новый признак администратора.

        Returns:
            User: Обновлённый пользователь.
        """
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if password is not None:
            user.hashed_password = hash_password(password)
        if is_admin is not None:
            user.is_admin = is_admin
        await db.flush()
        return user

    async def list_all(self, db: AsyncSession) -> Iterable[User]:
        """Возвращает список всех пользователей.

        Args:
            db (AsyncSession): Сессия БД.

        Returns:
            Iterable[User]: Пользователи.
        """
        return await super().list_all(db)

    async def list_all_paginated(
        self, db: AsyncSession, *, limit: int, offset: int
    ) -> list[User]:
        """Возвращает список пользователей с пагинацией.

        Args:
            db (AsyncSession): Сессия БД.
            limit (int): Максимум объектов.
            offset (int): Смещение.

        Returns:
            list[User]: Пользователи.
        """
        result = await db.execute(select(User).limit(limit).offset(offset))
        return result.scalars().all()


crud_user = CRUDUser()
