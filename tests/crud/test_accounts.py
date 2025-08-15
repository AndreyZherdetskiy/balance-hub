"""Unit-тесты для CRUD счетов."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.crud.accounts import CRUDAccount
from app.crud.users import CRUDUser
from tests.constants import TestMonetaryConstants, TestNumericConstants, TestUserData


class TestAccountsCRUD:
    """CRUD-сценарии для счетов."""

    @pytest.mark.asyncio()
    async def test_account_crud_flow(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест полного CRUD цикла для счетов."""
        users = CRUDUser()
        accounts = CRUDAccount()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            acc = await accounts.create_for_user(db, user.id)
            assert acc.user_id == user.id
            assert acc.balance == TestMonetaryConstants.AMOUNT_0_00

            fetched = await accounts.get_for_user(db, acc.id, user.id)
            assert fetched is not None and fetched.id == acc.id

            listed = await accounts.list_for_user(db, user.id)
            assert len(listed) == TestNumericConstants.COUNT_SINGLE
