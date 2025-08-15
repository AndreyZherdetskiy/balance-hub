"""CRUD-операции для счетов."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.account import Account


class CRUDAccount(CRUDBase[Account]):
    """CRUD-класс для модели `Account`."""

    def __init__(self) -> None:
        """Инициализирует CRUD-класс для модели `Account`.

        Args:
            model (type[Account]): Класс ORM-модели.
        """
        super().__init__(Account)

    async def get_for_user(
        self, db: AsyncSession, account_id: int, user_id: int
    ) -> Account | None:
        """Возвращает счёт по идентификатору и владельцу.

        Args:
            db (AsyncSession): Сессия БД.
            account_id (int): Идентификатор счёта.
            user_id (int): Идентификатор пользователя.

        Returns:
            Account | None: Счёт или None.
        """
        result = await db.execute(
            select(Account).where(Account.id == account_id, Account.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, db: AsyncSession, user_id: int) -> list[Account]:
        """Возвращает список счетов пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.

        Returns:
            list[Account]: Счета пользователя.
        """
        result = await db.execute(select(Account).where(Account.user_id == user_id))
        return result.scalars().all()

    async def list_for_user_paginated(
        self, db: AsyncSession, user_id: int, *, limit: int, offset: int
    ) -> list[Account]:
        """Возвращает список счетов пользователя с пагинацией.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.
            limit (int): Максимум объектов.
            offset (int): Смещение.

        Returns:
            list[Account]: Счета пользователя.
        """
        result = await db.execute(
            select(Account)
            .where(Account.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def create_for_user(self, db: AsyncSession, user_id: int) -> Account:
        """Создаёт счёт для пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.

        Returns:
            Account: Созданный счёт.

        Raises:
            ValueError: Если пользователь не найден.
        """
        account = Account(user_id=user_id)
        db.add(account)
        await db.flush()
        return account


crud_account = CRUDAccount()
