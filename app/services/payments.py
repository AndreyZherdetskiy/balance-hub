"""Бизнес-логика для работы с платежами."""

from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PaginationParams
from app.crud.payments import CRUDPayment
from app.models.payment import Payment


class PaymentService:
    """Сервис для работы с платежами."""

    def __init__(self, payments_crud: CRUDPayment):
        """Инициализирует сервис.

        Args:
            payments_crud: CRUD для платежей.
        """
        self.payments_crud = payments_crud

    async def get_user_payments(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = PaginationParams.DEFAULT_LIMIT,
        offset: int = PaginationParams.DEFAULT_OFFSET,
    ) -> List[Payment]:
        """Возвращает список платежей пользователя.

        Args:
            db (AsyncSession): Сессия БД.
            user_id (int): Идентификатор пользователя.
            limit (int): Максимум записей.
            offset (int): Смещение.

        Returns:
            list[Payment]: Список платежей пользователя.
        """
        payments = await self.payments_crud.list_for_user_paginated(
            db, user_id, limit=limit, offset=offset
        )
        return payments
