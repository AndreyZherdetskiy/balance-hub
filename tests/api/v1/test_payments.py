"""Тесты API платежей и вебхука - все сценарии."""

from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.crud.users import CRUDUser
from app.utils.crypto import compute_signature
from tests.constants import (
    TestAccountsPaths,
    TestPaymentsPaths,
    TestWebhookPaths,
    TestUserData,
    TestTransactionData,
    TestNumericConstants,
    TestMonetaryConstants,
    TestAuthData,
    TestValidationData,
    TestErrorMessages,
    TestDomainIds,
)


class TestPaymentsApi:
    """Тесты платежей и webhook."""

    @pytest.mark.asyncio()
    async def test_list_my_payments_empty(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.PAY_USER_EMAIL,
                full_name=TestUserData.PAY_USER_FULL_NAME,
                password=TestUserData.PAY_USER_PASSWORD,
            )
            user_id = user.id
            await db.commit()

        token = make_token(user_id)
        path = f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}"
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    @pytest.mark.asyncio()
    async def test_list_my_payments_success(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            user_id = user.id
            await db.commit()

        token = make_token(user_id)
        path = f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}"
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio()
    async def test_webhook_payment_and_list(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        settings = get_settings()
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.WH_USER_EMAIL,
                full_name=TestUserData.WH_USER_FULL_NAME,
                password=TestUserData.WH_USER_PASSWORD,
            )
            await db.commit()
        payload = {
            "transaction_id": TestDomainIds.WEBHOOK_TX_1,
            "user_id": user.id,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(TestMonetaryConstants.AMOUNT_100_00),
        }
        signature = compute_signature(
            account_id=payload["account_id"],
            amount=Decimal(payload["amount"]),
            transaction_id=payload["transaction_id"],
            user_id=payload["user_id"],
            secret_key=settings.webhook_secret_key,
        )
        payload["signature"] = signature

        wh_path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(wh_path, json=payload)
        assert resp.status_code == status.HTTP_201_CREATED
        body = resp.json()
        assert body["transaction_id"] == TestDomainIds.WEBHOOK_TX_1

        resp2 = await client.post(wh_path, json=payload)
        assert resp2.status_code == status.HTTP_409_CONFLICT
        assert TestErrorMessages.TRANSACTION_ALREADY_PROCESSED in resp2.json()["detail"]

        token = make_token(user.id)
        list_path = f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}"
        resp3 = await client.get(
            list_path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp3.status_code == status.HTTP_200_OK
        assert any(
            p["transaction_id"] == TestDomainIds.WEBHOOK_TX_1 for p in resp3.json()
        )

    @pytest.mark.asyncio()
    async def test_webhook_payment_success(
        self, client: AsyncClient, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.WEBHOOK_USER_EMAIL,
                full_name=TestUserData.WEBHOOK_USER_FULL_NAME,
                password=TestUserData.WEBHOOK_USER_PASSWORD,
            )
            await db.commit()

        settings = get_settings()
        payload = {
            "transaction_id": TestDomainIds.WEBHOOK_TX_1,
            "user_id": user.id,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(TestMonetaryConstants.AMOUNT_100_99),
        }

        signature = compute_signature(
            account_id=payload["account_id"],
            amount=Decimal(payload["amount"]),
            transaction_id=payload["transaction_id"],
            user_id=payload["user_id"],
            secret_key=settings.webhook_secret_key,
        )
        payload["signature"] = signature

        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(path, json=payload)
        assert resp.status_code == status.HTTP_201_CREATED
        body = resp.json()
        assert body["transaction_id"] == TestDomainIds.WEBHOOK_TX_1
        assert body["user_id"] == user.id
        assert body["amount"] == f"{TestMonetaryConstants.AMOUNT_100_99:.2f}"

    @pytest.mark.asyncio()
    async def test_webhook_payment_invalid_signature(self, client: AsyncClient) -> None:
        payload = {
            "transaction_id": TestDomainIds.TEST_TX_1,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(TestMonetaryConstants.AMOUNT_100_99),
            "signature": TestTransactionData.INVALID_SIGNATURE,
        }

        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(path, json=payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert TestErrorMessages.INVALID_SIGNATURE in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_webhook_payment_missing_signature(self, client: AsyncClient) -> None:
        payload = {
            "transaction_id": TestDomainIds.TEST_TX_1,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(TestMonetaryConstants.AMOUNT_100_99),
        }

        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(path, json=payload)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_webhook_payment_empty_signature(self, client: AsyncClient) -> None:
        payload = {
            "transaction_id": TestDomainIds.TEST_TX_1,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(TestMonetaryConstants.AMOUNT_100_99),
            "signature": TestTransactionData.EMPTY_SIGNATURE,
        }

        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(path, json=payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert TestErrorMessages.INVALID_SIGNATURE in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_webhook_payment_invalid_amount(self, client: AsyncClient) -> None:
        settings = get_settings()

        payload = {
            "transaction_id": TestDomainIds.TEST_TX_NEGATIVE,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(-TestMonetaryConstants.AMOUNT_100_99),
        }
        signature = compute_signature(
            account_id=payload["account_id"],
            amount=Decimal(payload["amount"]),
            transaction_id=payload["transaction_id"],
            user_id=payload["user_id"],
            secret_key=settings.webhook_secret_key,
        )
        payload["signature"] = signature

        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(path, json=payload)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_webhook_payment_zero_amount(self, client: AsyncClient) -> None:
        settings = get_settings()

        payload = {
            "transaction_id": TestDomainIds.TEST_TX_ZERO,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(TestMonetaryConstants.AMOUNT_0_00),
        }
        signature = compute_signature(
            account_id=payload["account_id"],
            amount=Decimal(payload["amount"]),
            transaction_id=payload["transaction_id"],
            user_id=payload["user_id"],
            secret_key=settings.webhook_secret_key,
        )
        payload["signature"] = signature

        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(path, json=payload)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_webhook_payment_missing_fields(self, client: AsyncClient) -> None:
        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(
            path,
            json={
                "user_id": TestDomainIds.TEST_USER_ID,
                "account_id": TestDomainIds.TEST_ACCOUNT_ID,
                "amount": str(TestMonetaryConstants.AMOUNT_100_99),
                "signature": TestTransactionData.TEST_SIGNATURE,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        resp = await client.post(
            path,
            json={
                "transaction_id": TestDomainIds.TEST_TX_1,
                "account_id": TestDomainIds.TEST_ACCOUNT_ID,
                "amount": str(TestMonetaryConstants.AMOUNT_100_99),
                "signature": TestTransactionData.TEST_SIGNATURE,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        resp = await client.post(
            path,
            json={
                "transaction_id": TestDomainIds.TEST_TX_1,
                "user_id": TestDomainIds.TEST_USER_ID,
                "amount": str(TestMonetaryConstants.AMOUNT_100_99),
                "signature": TestTransactionData.TEST_SIGNATURE,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        resp = await client.post(
            path,
            json={
                "transaction_id": TestDomainIds.TEST_TX_1,
                "user_id": TestDomainIds.TEST_USER_ID,
                "account_id": TestDomainIds.TEST_ACCOUNT_ID,
                "signature": TestTransactionData.TEST_SIGNATURE,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_webhook_payment_invalid_json(self, client: AsyncClient) -> None:
        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(
            path,
            content=TestValidationData.INVALID_JSON,
            headers={TestAuthData.CONTENT_TYPE_HEADER: TestAuthData.APPLICATION_JSON},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_webhook_payment_no_json(self, client: AsyncClient) -> None:
        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(path)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_list_my_payments_unauthorized(self, client: AsyncClient) -> None:
        path = f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}"
        resp = await client.get(path)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_list_my_payments_invalid_token(self, client: AsyncClient) -> None:
        path = f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}"
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{TestAuthData.INVALID_TOKEN}"
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_list_my_payments_malformed_auth_header(
        self, client: AsyncClient
    ) -> None:
        path = f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}"
        resp = await client.get(
            path,
            headers={TestAuthData.AUTHORIZATION_HEADER: TestAuthData.MALFORMED_AUTH},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_full_payment_flow_with_balance_update(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        settings = get_settings()
        users = CRUDUser()

        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.FLOW_TEST_EMAIL,
                full_name=TestUserData.FLOW_TEST_FULL_NAME,
                password=TestUserData.FLOW_TEST_PASSWORD,
            )
            await db.commit()
            token = make_token(user.id)

        list_path = f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}"
        resp = await client.get(
            list_path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

        async with test_sessionmaker() as db:
            admin_user = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            admin_token = make_token(admin_user.id)

        acc_path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
            user_id=user.id
        )
        resp = await client.post(
            acc_path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED
        account_id = resp.json()["id"]

        payload = {
            "transaction_id": TestDomainIds.INTEGRATION_TEST_TX_1,
            "user_id": user.id,
            "account_id": account_id,
            "amount": str(TestMonetaryConstants.AMOUNT_123_45),
        }
        signature = compute_signature(
            account_id=payload["account_id"],
            amount=Decimal(payload["amount"]),
            transaction_id=payload["transaction_id"],
            user_id=payload["user_id"],
            secret_key=settings.webhook_secret_key,
        )
        payload["signature"] = signature

        wh_path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp = await client.post(wh_path, json=payload)
        assert resp.status_code == status.HTTP_201_CREATED
        payment_data = resp.json()
        assert payment_data["transaction_id"] == TestDomainIds.INTEGRATION_TEST_TX_1
        assert payment_data["amount"] == f"{TestMonetaryConstants.AMOUNT_123_45:.2f}"

        resp = await client.get(
            list_path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        payments = resp.json()
        assert len(payments) == TestNumericConstants.COUNT_SINGLE
        assert payments[0]["transaction_id"] == TestDomainIds.INTEGRATION_TEST_TX_1
        assert payments[0]["amount"] == f"{TestMonetaryConstants.AMOUNT_123_45:.2f}"

    @pytest.mark.asyncio()
    async def test_webhook_idempotency_detailed(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        settings = get_settings()
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.IDEMPOTENT_EMAIL,
                full_name=TestUserData.IDEMPOTENT_FULL_NAME,
                password=TestUserData.IDEMPOTENT_PASSWORD,
            )
            await db.commit()

        payload = {
            "transaction_id": TestDomainIds.IDEMPOTENT_TX_UNIQUE,
            "user_id": user.id,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(TestMonetaryConstants.AMOUNT_999999_99),
        }
        signature = compute_signature(
            account_id=payload["account_id"],
            amount=Decimal(payload["amount"]),
            transaction_id=payload["transaction_id"],
            user_id=payload["user_id"],
            secret_key=settings.webhook_secret_key,
        )
        payload["signature"] = signature

        path = f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}"
        resp1 = await client.post(path, json=payload)
        assert resp1.status_code == status.HTTP_201_CREATED

        resp2 = await client.post(path, json=payload)
        assert resp2.status_code == status.HTTP_409_CONFLICT
        assert TestErrorMessages.TRANSACTION_ALREADY_PROCESSED in resp2.json()["detail"]

        resp3 = await client.post(path, json=payload)
        assert resp3.status_code == status.HTTP_409_CONFLICT
        assert TestErrorMessages.TRANSACTION_ALREADY_PROCESSED in resp3.json()["detail"]
