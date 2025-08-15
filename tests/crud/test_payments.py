"""Unit-тесты для CRUD платежей."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.crud.accounts import CRUDAccount
from app.crud.payments import CRUDPayment
from app.crud.users import CRUDUser
from tests.constants import (
    TestDomainIds,
    TestMonetaryConstants,
    TestNumericConstants,
    TestUserData,
)


class TestPaymentsCRUD:
    """CRUD-сценарии для платежей."""

    @pytest.mark.asyncio()
    async def test_payment_crud_flow(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест полного CRUD цикла для платежей."""
        users = CRUDUser()
        accounts = CRUDAccount()
        payments = CRUDPayment()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.PAY_USER_EMAIL,
                full_name=TestUserData.PAY_USER_FULL_NAME,
                password=TestUserData.PAY_USER_PASSWORD,
            )
            acc = await accounts.create_for_user(db, user.id)
            payment = await payments.create(
                db,
                transaction_id=TestDomainIds.TEST_TX_1,
                user_id=user.id,
                account_id=acc.id,
                amount=TestMonetaryConstants.AMOUNT_10_00,
            )
            assert payment.id is not None

            found = await payments.get_by_transaction(db, TestDomainIds.TEST_TX_1)
            assert found is not None and found.id == payment.id

            listed = await payments.list_for_user(db, user.id)
            assert len(listed) == TestNumericConstants.COUNT_SINGLE
