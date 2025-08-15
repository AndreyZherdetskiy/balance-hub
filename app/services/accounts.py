"""Бизнес-логика для работы со счетами пользователей."""

from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages, PaginationParams
from app.core.errors import NotFoundError
from app.crud.accounts import CRUDAccount
from app.crud.users import CRUDUser
from app.models.account import Account


class AccountService:
    """Сервис для работы со счетами пользователей."""

    def __init__(self, accounts_crud: CRUDAccount, users_crud: CRUDUser):
        """Инициализирует сервис.

        Args:
            accounts_crud (CRUDAccount): CRUD для счетов.
            users_crud (CRUDUser): CRUD для пользователей.
        """
        self.accounts_crud = accounts_crud
        self.users_crud = users_crud

    async def get_user_accounts(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = PaginationParams.DEFAULT_LIMIT,
        offset: int = PaginationParams.DEFAULT_OFFSET,
    ) -> List[Account]:
        """Возвращает список счетов пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.
            limit (int): Максимум записей.
            offset (int): Смещение.

        Returns:
            list[Account]: Список счетов пользователя.

        Raises:
            NotFoundError: Если пользователь не найден.
        """
        user = await self.users_crud.get(db, user_id)
        if not user:
            raise NotFoundError(ErrorMessages.USER_NOT_FOUND)

        accounts = await self.accounts_crud.list_for_user_paginated(
            db, user_id, limit=limit, offset=offset
        )
        return accounts

    async def create_account_for_user(self, db: AsyncSession, user_id: int) -> Account:
        """Создаёт новый счёт для пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.

        Returns:
            Account: Созданный счёт.

        Raises:
            NotFoundError: Если пользователь не найден.
        """
        user = await self.users_crud.get(db, user_id)
        if not user:
            raise NotFoundError(ErrorMessages.USER_NOT_FOUND)

        account = await self.accounts_crud.create_for_user(db, user_id)
        await db.commit()
        await db.refresh(account)
        return account
