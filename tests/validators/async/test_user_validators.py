from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants import ErrorMessages
from tests.constants import TestUserData, TestDomainIds
from app.core.errors import ValidationError, NotFoundError
from app.crud.users import CRUDUser
from app.validators.async_.users import UserAsyncValidator


class TestUserAsyncValidator:
    @pytest.fixture
    def validator(self) -> UserAsyncValidator:
        return UserAsyncValidator(CRUDUser())

    @pytest.mark.asyncio()
    async def test_assert_email_unique_ok(
        self,
        validator: UserAsyncValidator,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        async with test_sessionmaker() as db:
            await validator.assert_email_unique(db, TestUserData.NEW_EMAIL_GENERIC)

    @pytest.mark.asyncio()
    async def test_assert_email_unique_raises_when_taken(
        self,
        validator: UserAsyncValidator,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        async with test_sessionmaker() as db:
            users = CRUDUser()
            await users.create(
                db,
                email=TestUserData.EXISTING_EMAIL,
                full_name=TestUserData.EXISTING_FULL_NAME,
                password=TestUserData.EXISTING_PASSWORD,
            )
            with pytest.raises(
                ValidationError, match=ErrorMessages.EMAIL_ALREADY_EXISTS
            ):
                await validator.assert_email_unique(db, TestUserData.EXISTING_EMAIL)

    @pytest.mark.asyncio()
    async def test_assert_email_unique_exclude_user_id_allows_self(
        self,
        validator: UserAsyncValidator,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        async with test_sessionmaker() as db:
            users = CRUDUser()
            user = await users.create(
                db,
                email=TestUserData.JOHN_EMAIL,
                full_name=TestUserData.JOHN_FULL_NAME,
                password=TestUserData.PASS_123,
            )
            await validator.assert_email_unique(
                db, TestUserData.JOHN_EMAIL, exclude_user_id=user.id
            )

    @pytest.mark.asyncio()
    async def test_get_user_or_error_found(
        self,
        validator: UserAsyncValidator,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        async with test_sessionmaker() as db:
            users = CRUDUser()
            created = await users.create(
                db,
                email=TestUserData.JOHNNY_EMAIL,
                full_name=TestUserData.JOHNNY_NAME,
                password=TestUserData.PASS_123,
            )
            got = await validator.get_user_or_error(db, created.id)
            assert got.id == created.id
            assert got.email == TestUserData.JOHNNY_EMAIL

    @pytest.mark.asyncio()
    async def test_get_user_or_error_not_found(
        self,
        validator: UserAsyncValidator,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        async with test_sessionmaker() as db:
            with pytest.raises(NotFoundError, match=ErrorMessages.USER_NOT_FOUND):
                await validator.get_user_or_error(db, TestDomainIds.NONEXISTENT_USER_ID)
