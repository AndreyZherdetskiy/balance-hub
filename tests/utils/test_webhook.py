"""Тесты утилит вебхука - все сценарии."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.errors import DuplicateTransactionError
from app.crud.accounts import CRUDAccount
from app.crud.payments import CRUDPayment
from app.crud.users import CRUDUser
from app.services.webhook import WebhookService
from app.utils.crypto import compute_signature
from app.validators.async_ import UserAsyncValidator
from tests.constants import (
    TestDomainConstraints,
    TestDomainIds,
    TestMonetaryConstants,
    TestNumericConstants,
    TestTransactionData,
    TestUserData,
    TestValidationData,
)


class TestComputeSignature:
    """Тесты для функции compute_signature."""

    def test_stable(self) -> None:
        """Тест стабильности подписи."""
        sig1 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        sig2 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        assert sig1 == sig2

    def test_different_account_id(self) -> None:
        """Тест различных подписей для разных account_id."""
        sig1 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        sig2 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID + 1,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        assert sig1 != sig2

    def test_different_amount(self) -> None:
        """Тест различных подписей для разных сумм."""
        sig1 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        sig2 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_200_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        assert sig1 != sig2

    def test_different_transaction_id(self) -> None:
        """Тест различных подписей для разных transaction_id."""
        sig1 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        sig2 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_2,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        assert sig1 != sig2

    def test_different_user_id(self) -> None:
        """Тест различных подписей для разных user_id."""
        sig1 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        sig2 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42 + 1,
            TestTransactionData.SECRET_KEY,
        )
        assert sig1 != sig2

    def test_different_secret(self) -> None:
        """Тест различных подписей для разных секретов."""
        sig1 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY_1,
        )
        sig2 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY_2,
        )
        assert sig1 != sig2

    def test_zero_values(self) -> None:
        """Тест подписи с нулевыми значениями."""
        sig = compute_signature(
            TestNumericConstants.COUNT_EMPTY,
            TestMonetaryConstants.AMOUNT_0_00,
            TestTransactionData.EMPTY_SIGNATURE,
            TestNumericConstants.COUNT_EMPTY,
            TestTransactionData.EMPTY_SIGNATURE,
        )
        assert isinstance(sig, str)
        assert len(sig) == 64

    def test_negative_values(self) -> None:
        """Тест подписи с отрицательными значениями."""
        sig = compute_signature(
            TestNumericConstants.NEGATIVE_ONE,
            TestMonetaryConstants.AMOUNT_NEG_100_00,
            TestDomainIds.TEST_TX_NEGATIVE,
            -TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        assert isinstance(sig, str)
        assert len(sig) == 64

    def test_large_values(self) -> None:
        """Тест подписи с большими значениями."""
        sig = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_999999_99,
            TestDomainIds.VERY_LONG_TRANSACTION_ID,
            TestDomainConstraints.MAX_INT32,
            TestTransactionData.SECRET_LONG,
        )
        assert isinstance(sig, str)
        assert len(sig) == 64

    def test_unicode_data(self) -> None:
        """Тест подписи с Unicode данными."""
        sig = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TX_UNICODE_RU,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_UNICODE_RU,
        )
        assert isinstance(sig, str)
        assert len(sig) == 64

    def test_special_chars(self) -> None:
        """Тест подписи со специальными символами."""
        sig = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TX_SPECIAL,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_SPECIAL,
        )
        assert isinstance(sig, str)
        assert len(sig) == 64

    def test_decimal_precision(self) -> None:
        """Тест подписи с различной точностью Decimal."""
        sig1 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_0,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        sig2 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_00,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        sig3 = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_100_000,
            TestDomainIds.TEST_TX_1,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )

        assert sig1 == sig2 == sig3

    def test_very_small_decimal(self) -> None:
        """Тест подписи с очень маленьким Decimal."""
        sig = compute_signature(
            TestDomainIds.TEST_ACCOUNT_ID,
            TestMonetaryConstants.AMOUNT_0_01,
            TestDomainIds.TX_SMALL,
            TestNumericConstants.INT_42,
            TestTransactionData.SECRET_KEY,
        )
        assert isinstance(sig, str)
        assert len(sig) == 64


class TestProcessTopup:
    """Тесты для функции process_topup."""

    @pytest.mark.asyncio()
    async def test_idempotent(self, test_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        """Тест идемпотентности process_topup."""
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.TOPUP_EMAIL,
                full_name=TestUserData.TOPUP_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment1 = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_UNIQUE,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_50_25,
            )
            await db.refresh(payment1)
            assert payment1.transaction_id == TestDomainIds.TX_UNIQUE

            # Второй вызов должен вызвать исключение
            with pytest.raises(DuplicateTransactionError):
                await service.process_topup(
                    db,
                    transaction_id=TestDomainIds.TX_UNIQUE,
                    account_id=payment1.account_id,
                    user_id=user.id,
                    amount=TestMonetaryConstants.AMOUNT_50_25,
                )

    @pytest.mark.asyncio()
    async def test_creates_account_when_needed(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания счета когда account_id = 0."""
        async with test_sessionmaker() as db:
            users = CRUDUser()
            user = await users.create(
                db,
                email=TestUserData.NEED_EMAIL,
                full_name=TestUserData.NEED_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )
            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_NEW_ACCOUNT,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_100_00,
            )

            assert payment.account_id > TestNumericConstants.COUNT_EMPTY
            assert payment.user_id == TestDomainIds.TEST_USER_ID
            assert payment.amount == TestMonetaryConstants.AMOUNT_100_00

    @pytest.mark.asyncio()
    async def test_with_existing_account(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест пополнения существующего счета."""
        async with test_sessionmaker() as db:
            users = CRUDUser()
            accounts = CRUDAccount()

            user = await users.create(
                db,
                email=TestUserData.TEST_EMAIL_GENERIC,
                full_name=TestValidationData.TEST_USER_FULL_NAME,
                password=TestUserData.PASSWORD_LOWER_123,
            )
            account = await accounts.create_for_user(db, user.id)
            initial_balance = account.balance

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_EXISTING_ACCOUNT,
                account_id=account.id,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_200_00,
            )

            await db.refresh(account)
            assert account.balance == initial_balance + TestMonetaryConstants.AMOUNT_200_00
            assert payment.account_id == account.id

    @pytest.mark.asyncio()
    async def test_creates_new_account_when_mismatch(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания нового счета при несоответствии account_id и user_id."""
        async with test_sessionmaker() as db:
            users = CRUDUser()
            accounts = CRUDAccount()

            user1 = await users.create(
                db,
                email=TestUserData.USER1_EMAIL,
                full_name=TestUserData.FIRST_USER,
                password=TestUserData.PASSWORD_LOWER_123,
            )
            user2 = await users.create(
                db,
                email=TestUserData.USER2_EMAIL,
                full_name=TestUserData.SECOND_USER,
                password=TestUserData.PASSWORD_LOWER_123,
            )
            account1 = await accounts.create_for_user(db, user1.id)

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_MISMATCH,
                account_id=account1.id,
                user_id=user2.id,
                amount=TestMonetaryConstants.AMOUNT_150_00,
            )

            assert payment.account_id != account1.id
            assert payment.user_id == user2.id
            assert payment.amount == TestMonetaryConstants.AMOUNT_150_00

    @pytest.mark.asyncio()
    async def test_different_amounts(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест пополнений с разными суммами."""
        async with test_sessionmaker() as db:
            users = CRUDUser()
            user1 = await users.create(
                db,
                email=TestUserData.SMALL_EMAIL,
                full_name=TestUserData.SMALL_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )
            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment1 = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_SMALL,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user1.id,
                amount=TestMonetaryConstants.AMOUNT_0_01,
            )
            assert payment1.amount == TestMonetaryConstants.AMOUNT_0_01

            user2 = await users.create(
                db,
                email=TestUserData.LARGE_EMAIL,
                full_name=TestUserData.LARGE_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )
            payment2 = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_BIG,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user2.id,
                amount=TestMonetaryConstants.AMOUNT_999999_99,
            )
            assert payment2.amount == TestMonetaryConstants.AMOUNT_999999_99

            user3 = await users.create(
                db,
                email=TestUserData.PRECISE_EMAIL,
                full_name=TestUserData.PRECISE_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )
            payment3 = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_PRECISE,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user3.id,
                amount=TestMonetaryConstants.PRECISE_123_123456789,
            )
            assert payment3.amount == TestMonetaryConstants.AMOUNT_123_12

    @pytest.mark.asyncio()
    async def test_creates_account_when_missing(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания счета когда он отсутствует."""
        users = CRUDUser()
        accounts = CRUDAccount()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.NOACCOUNT_EMAIL,
                full_name=TestUserData.NOACCOUNT_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            user_accounts = await accounts.list_for_user(db, user.id)
            assert len(user_accounts) == 0

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_CREATE_ACCOUNT,
                account_id=TestDomainIds.NONEXISTENT_ACCOUNT_ID,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_75_00,
            )

            user_accounts = await accounts.list_for_user(db, user.id)
            assert len(user_accounts) == 1
            assert user_accounts[0].id == payment.account_id
            assert user_accounts[0].balance == TestMonetaryConstants.AMOUNT_75_00

    @pytest.mark.asyncio()
    async def test_uses_existing_account(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест использования существующего счета."""
        users = CRUDUser()
        accounts = CRUDAccount()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.EXISTING_EMAIL_2,
                full_name=TestUserData.EXISTING_FULL_NAME_2,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            account = await accounts.create_for_user(db, user.id)
            original_balance = account.balance

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_EXISTING_ACCOUNT,
                account_id=account.id,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_25_00,
            )

            assert payment.account_id == account.id

            await db.refresh(account)
            expected_balance = (
                original_balance or TestMonetaryConstants.ZERO_TWO_PLACES
            ) + TestMonetaryConstants.AMOUNT_25_00
            assert account.balance == expected_balance

    @pytest.mark.asyncio()
    async def test_updates_balance_correctly(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест корректного обновления баланса."""
        users = CRUDUser()
        accounts = CRUDAccount()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.BALANCE_EMAIL,
                full_name=TestUserData.BALANCE_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            account = await accounts.create_for_user(db, user.id)
            account.balance = TestMonetaryConstants.AMOUNT_100_00
            await db.commit()

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_BALANCE_1,
                account_id=account.id,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_50_25,
            )

            await db.refresh(account)
            assert account.balance == (
                TestMonetaryConstants.AMOUNT_100_00 + TestMonetaryConstants.AMOUNT_50_25
            )

            await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_BALANCE_2,
                account_id=account.id,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_25_50,
            )

            await db.refresh(account)
            assert account.balance == (
                TestMonetaryConstants.AMOUNT_100_00
                + TestMonetaryConstants.AMOUNT_50_25
                + TestMonetaryConstants.AMOUNT_25_50
            )

    @pytest.mark.asyncio()
    async def test_zero_amount(self, test_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        """Тест пополнения на нулевую сумму."""
        users = CRUDUser()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.ZERO_EMAIL,
                full_name=TestUserData.ZERO_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_ZERO,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_0_00,
            )

            assert payment.amount == TestMonetaryConstants.AMOUNT_0_00
            assert payment.transaction_id == TestDomainIds.TX_ZERO

    @pytest.mark.asyncio()
    async def test_large_amount(self, test_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        """Тест пополнения на большую сумму."""
        users = CRUDUser()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.LARGE_EMAIL,
                full_name=TestUserData.LARGE_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            large_amount = TestMonetaryConstants.AMOUNT_999999999999999_99
            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_BIG,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user.id,
                amount=large_amount,
            )

            assert payment.amount == large_amount

    @pytest.mark.asyncio()
    async def test_decimal_precision(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест пополнения с точностью до копеек."""
        users = CRUDUser()
        accounts = CRUDAccount()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.PRECISE_EMAIL,
                full_name=TestUserData.PRECISE_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            account = await accounts.create_for_user(db, user.id)
            account.balance = TestMonetaryConstants.AMOUNT_10_01
            await db.commit()

            precise_amount = TestMonetaryConstants.AMOUNT_15_99
            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_PRECISION,
                account_id=account.id,
                user_id=user.id,
                amount=precise_amount,
            )

            await db.refresh(account)
            assert account.balance == TestMonetaryConstants.AMOUNT_26_00

    @pytest.mark.asyncio()
    async def test_duplicate_transaction_id_returns_existing(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест что повторный transaction_id возвращает существующий платеж.

        Глобальная уникальность.
        """
        users = CRUDUser()

        async with test_sessionmaker() as db:
            user1 = await users.create(
                db,
                email=TestUserData.USER1_EMAIL,
                full_name=TestUserData.FIRST_USER,
                password=TestUserData.PASSWORD_123_STRONG,
            )
            user2 = await users.create(
                db,
                email=TestUserData.USER2_EMAIL,
                full_name=TestUserData.SECOND_USER,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            user1_id = user1.id
            user2_id = user2.id

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment1 = await service.process_topup(
                db,
                transaction_id=TestDomainIds.UNIQUE_GLOBAL_TX,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user1_id,
                amount=TestMonetaryConstants.AMOUNT_100_00,
            )

            # Второй вызов должен вызвать исключение
            with pytest.raises(DuplicateTransactionError):
                await service.process_topup(
                    db,
                    transaction_id=TestDomainIds.UNIQUE_GLOBAL_TX,
                    account_id=TestDomainIds.TEST_ACCOUNT_ID,
                    user_id=user2_id,
                    amount=TestMonetaryConstants.AMOUNT_200_00,
                )

            payment1_user_id = payment1.user_id
            payment1_amount = payment1.amount

        # Проверяем, что первый платеж создался корректно
        assert payment1_user_id == user1_id
        assert payment1_amount == TestMonetaryConstants.AMOUNT_100_00

    @pytest.mark.asyncio()
    async def test_rollback_on_error(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест отката транзакции при ошибке."""
        users = CRUDUser()
        payments = CRUDPayment()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.ROLLBACK_EMAIL,
                full_name=TestUserData.ROLLBACK_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            await payments.create(
                db,
                transaction_id=TestDomainIds.DUPLICATE_TX,
                user_id=user.id,
                account_id=TestDomainIds.TEST_ACCOUNT_ID_NEXT,
                amount=TestMonetaryConstants.AMOUNT_50_25,
            )
            await db.commit()

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            # Повторный вызов должен вызвать исключение
            with pytest.raises(DuplicateTransactionError):
                await service.process_topup(
                    db,
                    transaction_id=TestDomainIds.DUPLICATE_TX,
                    account_id=TestDomainIds.TEST_ACCOUNT_ID,
                    user_id=user.id,
                    amount=TestMonetaryConstants.AMOUNT_75_00,
                )

            # Проверяем, что оригинальный платеж не изменился
            original_payment = await payments.get_by_transaction(db, TestDomainIds.DUPLICATE_TX)
            assert original_payment.amount == TestMonetaryConstants.AMOUNT_50_25
            assert original_payment.transaction_id == TestDomainIds.DUPLICATE_TX

    @pytest.mark.asyncio()
    async def test_creates_payment_record(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания записи платежа."""
        users = CRUDUser()
        payments = CRUDPayment()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.PAYMENT_EMAIL,
                full_name=TestUserData.PAYMENT_FULL_NAME,
                password=TestUserData.PASSWORD_123_STRONG,
            )

            user_payments = await payments.list_for_user(db, user.id)
            assert len(user_payments) == 0

            service = WebhookService(CRUDAccount(), CRUDPayment(), UserAsyncValidator(CRUDUser()))
            payment = await service.process_topup(
                db,
                transaction_id=TestDomainIds.TX_PAYMENT_RECORD,
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                user_id=user.id,
                amount=TestMonetaryConstants.AMOUNT_30_00,
            )

            user_payments = await payments.list_for_user(db, user.id)
            assert len(user_payments) == 1
            assert user_payments[0].id == payment.id
            assert user_payments[0].transaction_id == TestDomainIds.TX_PAYMENT_RECORD
            assert user_payments[0].amount == TestMonetaryConstants.AMOUNT_30_00
            assert user_payments[0].user_id == user.id
