"""Сервис обработки вебхуков внешней платежной системы.

Инкапсулирует бизнес-логику приёма платежа пополнения и работу с моделями.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MonetaryConstants
from app.core.errors import DuplicateTransactionError
from app.crud.accounts import CRUDAccount
from app.crud.payments import CRUDPayment
from app.models.payment import Payment
from app.validators.async_ import UserAsyncValidator


class WebhookService:
    """Сервис работы с вебхуками платежей."""

    def __init__(
        self,
        accounts_crud: CRUDAccount,
        payments_crud: CRUDPayment,
        user_validator: UserAsyncValidator,
    ):
        """Инициализирует сервис вебхуков.

        Args:
            accounts_crud: CRUD-уровень для работы с счетами.
            payments_crud: CRUD-уровень для работы с платежами.
            user_validator: Валидатор пользователей для проверки существования.
        """
        self.accounts_crud = accounts_crud
        self.payments_crud = payments_crud
        self.user_validator = user_validator

    async def process_topup(
        self,
        db: AsyncSession,
        *,
        transaction_id: str,
        account_id: int,
        user_id: int,
        amount: Decimal,
    ) -> Payment:
        """Идемпотентно обрабатывает вебхук пополнения.

        Шаги:
            1. Проверить существование транзакции (идемпотентность).
            2. Найти счет пользователя или создать новый.
            3. Создать запись платежа.
            4. Начислить сумму на баланс и закоммитить транзакцию.

        Args:
            db (AsyncSession): Сессия БД.
            transaction_id (str): Внешний идентификатор транзакции (идемпотентность).
            account_id (int): Идентификатор счёта (может отсутствовать).
            user_id (int): Идентификатор пользователя.
            amount (Decimal): Сумма пополнения.

        Returns:
            Payment: Созданный платёж.

        Raises:
            IntegrityError: Если транзакция уже существует.
        """
        # 1. Проверяем идемпотентность ДО создания
        existing_payment = await self.payments_crud.get_by_transaction(
            db, transaction_id
        )
        if existing_payment is not None:
            raise DuplicateTransactionError()

        # 2. Находим или создаем счет
        account = None
        if account_id:
            account = await self.accounts_crud.get_for_user(db, account_id, user_id)
        if not account:
            await self.user_validator.get_user_or_error(db, user_id)
            account = await self.accounts_crud.create_for_user(db, user_id)

        # 3. Создаем платеж и обновляем баланс
        payment = await self.payments_crud.create(
            db,
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account.id,
            amount=amount,
        )
        account.balance = (
            account.balance or MonetaryConstants.ZERO_TWO_PLACES
        ) + amount
        await db.commit()

        await db.refresh(payment)
        return payment
