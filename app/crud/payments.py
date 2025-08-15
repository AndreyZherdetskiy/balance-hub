"""CRUD-операции для платежей."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.payment import Payment


class CRUDPayment(CRUDBase[Payment]):
    """CRUD-класс для модели `Payment`."""

    def __init__(self) -> None:
        """Инициализирует CRUD-класс для модели `Payment`.

        Args:
            model (type[Payment]): Класс ORM-модели.
        """
        super().__init__(Payment)

    async def get_by_transaction(self, db: AsyncSession, transaction_id: str) -> Payment | None:
        """Возвращает платёж по идентификатору транзакции.

        Args:
            db (AsyncSession): Сессия БД.
            transaction_id (str): Внешний идентификатор транзакции.

        Returns:
            Payment | None: Платёж или None.
        """
        result = await db.execute(select(Payment).where(Payment.transaction_id == transaction_id))
        return result.scalar_one_or_none()

    async def list_for_user(self, db: AsyncSession, user_id: int) -> list[Payment]:
        """Возвращает список платежей пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.

        Returns:
            list[Payment]: Платежи пользователя.
        """
        result = await db.execute(select(Payment).where(Payment.user_id == user_id))
        return result.scalars().all()

    async def list_for_user_paginated(
        self, db: AsyncSession, user_id: int, *, limit: int, offset: int
    ) -> list[Payment]:
        """Возвращает список платежей пользователя с пагинацией.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.
            limit (int): Максимум объектов.
            offset (int): Смещение.

        Returns:
            list[Payment]: Платежи пользователя.
        """
        result = await db.execute(
            select(Payment).where(Payment.user_id == user_id).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        transaction_id: str,
        user_id: int,
        account_id: int,
        amount,
    ) -> Payment:
        """Создаёт платёж.

        Args:
            db (AsyncSession): Сессия БД.
            transaction_id (str): Идентификатор транзакции.
            user_id (int): Идентификатор пользователя.
            account_id (int): Идентификатор счета.
            amount: Сумма.

        Returns:
            Payment: Созданный платёж.
        """
        payment = Payment(
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account_id,
            amount=amount,
        )
        db.add(payment)
        await db.flush()
        return payment


crud_payment = CRUDPayment()
