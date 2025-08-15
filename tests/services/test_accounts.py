"""Тесты для AccountService."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants import ErrorMessages, PaginationParams
from app.core.errors import NotFoundError
from app.crud.accounts import CRUDAccount
from app.crud.users import CRUDUser
from app.models.account import Account
from app.services.accounts import AccountService
from tests.constants import (
    TestDomainIds,
    TestMonetaryConstants,
    TestNumericConstants,
    TestUserData,
    TestValidationData,
)


class TestAccountService:
    """Тесты для AccountService."""

    @pytest.fixture
    def account_service(self) -> AccountService:
        """Создает экземпляр AccountService."""
        return AccountService(accounts_crud=CRUDAccount(), users_crud=CRUDUser())

    @pytest.mark.asyncio()
    async def test_get_user_accounts_success(
        self,
        account_service: AccountService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест успешного получения счетов пользователя."""
        # Создаем пользователя
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.TEST_EMAIL_GENERIC,
                full_name=TestValidationData.TEST_USER_FULL_NAME,
                password=TestUserData.SECURE_PASSWORD_123,
            )
            await db.commit()

            # Создаем счета для пользователя
            accounts_crud = CRUDAccount()
            await accounts_crud.create_for_user(db, user.id)
            await accounts_crud.create_for_user(db, user.id)
            await db.commit()

            # Получаем счета
            result = await account_service.get_user_accounts(db, user.id)

            assert len(result) == TestNumericConstants.COUNT_TWO
            assert all(isinstance(acc, Account) for acc in result)
            assert all(acc.user_id == user.id for acc in result)

    @pytest.mark.asyncio()
    async def test_get_user_accounts_user_not_found(
        self,
        account_service: AccountService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест получения счетов несуществующего пользователя."""
        async with test_sessionmaker() as db:
            with pytest.raises(NotFoundError, match=ErrorMessages.USER_NOT_FOUND):
                await account_service.get_user_accounts(
                    db, TestDomainIds.NONEXISTENT_USER_ID
                )

    @pytest.mark.asyncio()
    async def test_get_user_accounts_with_pagination(
        self,
        account_service: AccountService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест получения счетов с пагинацией."""
        # Создаем пользователя
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.PAGINATION_EMAIL,
                full_name=TestUserData.PAGINATION_FULL_NAME,
                password=TestUserData.SECURE_PASSWORD_123,
            )
            await db.commit()

            # Создаем 5 счетов
            accounts_crud = CRUDAccount()
            await accounts_crud.create_for_user(db, user.id)
            await accounts_crud.create_for_user(db, user.id)
            await accounts_crud.create_for_user(db, user.id)
            await accounts_crud.create_for_user(db, user.id)
            await accounts_crud.create_for_user(db, user.id)
            await db.commit()

            # Тестируем пагинацию
            result = await account_service.get_user_accounts(
                db, user.id, limit=2, offset=0
            )
            assert len(result) == TestNumericConstants.COUNT_TWO

            result = await account_service.get_user_accounts(
                db, user.id, limit=2, offset=2
            )
            assert len(result) == TestNumericConstants.COUNT_TWO

            result = await account_service.get_user_accounts(
                db, user.id, limit=2, offset=4
            )
            assert len(result) == TestNumericConstants.COUNT_SINGLE

    @pytest.mark.asyncio()
    async def test_get_user_accounts_default_pagination(
        self,
        account_service: AccountService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест получения счетов с параметрами пагинации по умолчанию."""
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.DEFAULT_PAGINATION_EMAIL,
                full_name=TestUserData.DEFAULT_PAGINATION_FULL_NAME,
                password=TestUserData.SECURE_PASSWORD_123,
            )
            await db.commit()

            # Создаем счета
            accounts_crud = CRUDAccount()
            await accounts_crud.create_for_user(db, user.id)
            await accounts_crud.create_for_user(db, user.id)
            await accounts_crud.create_for_user(db, user.id)
            await db.commit()

            # Получаем счета без указания параметров пагинации
            result = await account_service.get_user_accounts(db, user.id)

            # Проверяем, что используются значения по умолчанию
            assert len(result) <= PaginationParams.DEFAULT_LIMIT

    @pytest.mark.asyncio()
    async def test_create_account_for_user_success(
        self,
        account_service: AccountService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест успешного создания счета для пользователя."""
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.CREATE_ACCOUNT_EMAIL,
                full_name=TestUserData.CREATE_ACCOUNT_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )
            await db.commit()

            # Создаем счет
            result = await account_service.create_account_for_user(db, user.id)

            assert isinstance(result, Account)
            assert result.user_id == user.id
            assert result.balance == TestMonetaryConstants.AMOUNT_0_00

    @pytest.mark.asyncio()
    async def test_create_account_user_not_found(
        self,
        account_service: AccountService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест создания счета для несуществующего пользователя."""
        async with test_sessionmaker() as db:
            with pytest.raises(NotFoundError, match=ErrorMessages.USER_NOT_FOUND):
                await account_service.create_account_for_user(
                    db, TestDomainIds.NONEXISTENT_USER_ID
                )

    @pytest.mark.asyncio()
    async def test_create_multiple_accounts_for_user(
        self,
        account_service: AccountService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест создания нескольких счетов для одного пользователя."""
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.MULTIPLE_ACCOUNTS_EMAIL,
                full_name=TestUserData.MULTIPLE_ACCOUNTS_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )
            await db.commit()

            # Создаем несколько счетов
            account1 = await account_service.create_account_for_user(db, user.id)
            account2 = await account_service.create_account_for_user(db, user.id)
            account3 = await account_service.create_account_for_user(db, user.id)

            # Проверяем, что все счета созданы
            assert account1.id != account2.id
            assert account2.id != account3.id
            assert all(acc.user_id == user.id for acc in [account1, account2, account3])
            assert all(
                acc.balance == TestMonetaryConstants.AMOUNT_0_00
                for acc in [account1, account2, account3]
            )

    @pytest.mark.asyncio()
    async def test_account_service_dependency_injection(
        self,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест правильной работы dependency injection в AccountService."""
        # Создаем мок CRUD объекты
        mock_accounts_crud = CRUDAccount()
        mock_users_crud = CRUDUser()

        service = AccountService(
            accounts_crud=mock_accounts_crud, users_crud=mock_users_crud
        )

        assert service.accounts_crud is mock_accounts_crud
        assert service.users_crud is mock_users_crud
