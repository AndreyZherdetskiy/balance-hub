"""Интеграционные тесты полного flow работы с пользователями, счетами и платежами.

Тестирует комплексные сценарии, включающие:
- Создание пользователей (обычных и админов)
- Создание счетов для пользователей
- Обработку webhook платежей
- Проверку балансов и истории платежей
- Административные операции
"""

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
    TestAuthData,
    TestDomainIds,
    TestErrorMessages,
    TestMonetaryConstants,
    TestNumericConstants,
    TestPaymentsPaths,
    TestTransactionData,
    TestUserData,
    TestUsersPaths,
    TestWebhookPaths,
)


class TestIntegrationFullFlow:
    """Интеграционные тесты полного flow работы с системой."""

    @pytest.mark.asyncio()
    async def test_complete_user_lifecycle_with_payments(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        """Полный жизненный цикл пользователя: создание, счета, платежи, обновления."""
        settings = get_settings()
        users = CRUDUser()

        # 1. Создаем администратора
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            admin_token = make_token(admin.id)

        # 2. Админ создает обычного пользователя
        user_data = {
            "email": TestUserData.INTEGRATION_EMAIL,
            "full_name": TestUserData.INTEGRATION_FULL_NAME,
            "password": TestUserData.INTEGRATION_PASSWORD,
            "is_admin": False,
        }

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
            json=user_data,
        )
        assert resp.status_code == status.HTTP_201_CREATED
        created_user = resp.json()
        user_id = created_user["id"]
        assert created_user["email"] == user_data["email"]
        assert created_user["full_name"] == user_data["full_name"]
        assert created_user["is_admin"] is False

        # 3. Админ создает счет для пользователя
        resp = await client.post(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
                user_id=user_id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED
        account_data = resp.json()
        account_id = account_data["id"]
        assert account_data["user_id"] == user_id
        assert account_data["balance"] == f"{TestMonetaryConstants.AMOUNT_0_00:.2f}"

        # 4. Проверяем, что пользователь может видеть свой счет
        user_token = make_token(user_id)
        resp = await client.get(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
                user_id=user_id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        user_accounts = resp.json()
        assert len(user_accounts) == TestNumericConstants.COUNT_SINGLE
        assert user_accounts[0]["id"] == account_id

        # 5. Обрабатываем webhook платеж
        webhook_payload = {
            "transaction_id": TestDomainIds.INTEGRATION_TX_001,
            "user_id": user_id,
            "account_id": account_id,
            "amount": str(TestMonetaryConstants.AMOUNT_150_00),
        }
        signature = compute_signature(
            account_id=webhook_payload["account_id"],
            amount=Decimal(webhook_payload["amount"]),
            transaction_id=webhook_payload["transaction_id"],
            user_id=webhook_payload["user_id"],
            secret_key=settings.webhook_secret_key,
        )
        webhook_payload["signature"] = signature

        resp = await client.post(
            f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}",
            json=webhook_payload,
        )
        assert resp.status_code == status.HTTP_201_CREATED
        payment_data = resp.json()
        assert payment_data["transaction_id"] == TestDomainIds.INTEGRATION_TX_001
        assert payment_data["amount"] == f"{TestMonetaryConstants.AMOUNT_150_00:.2f}"

        # 6. Проверяем обновление баланса счета
        resp = await client.get(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
                user_id=user_id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        updated_accounts = resp.json()
        assert (
            updated_accounts[0]["balance"]
            == f"{TestMonetaryConstants.AMOUNT_150_00:.2f}"
        )

        # 7. Проверяем историю платежей пользователя
        resp = await client.get(
            f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        payments = resp.json()
        assert len(payments) == TestNumericConstants.COUNT_SINGLE
        assert payments[0]["transaction_id"] == TestDomainIds.INTEGRATION_TX_001
        assert payments[0]["amount"] == f"{TestMonetaryConstants.AMOUNT_150_00:.2f}"

        # 8. Админ обновляет информацию о пользователе
        update_data = {"full_name": TestUserData.INTEGRATION_UPDATED_NAME}
        resp = await client.patch(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=user_id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
            json=update_data,
        )
        assert resp.status_code == status.HTTP_200_OK
        updated_user = resp.json()
        assert updated_user["full_name"] == TestUserData.INTEGRATION_UPDATED_NAME

        # 9. Проверяем, что пользователь может получить свою обновленную информацию
        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        me_data = resp.json()
        assert me_data["full_name"] == TestUserData.INTEGRATION_UPDATED_NAME
        assert me_data["email"] == TestUserData.INTEGRATION_EMAIL

        # 10. Админ создает второй счет для пользователя
        resp = await client.post(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
                user_id=user_id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED
        second_account = resp.json()
        second_account_id = second_account["id"]
        assert second_account["user_id"] == user_id

        # 11. Проверяем, что у пользователя теперь два счета
        resp = await client.get(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
                user_id=user_id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        all_accounts = resp.json()
        assert len(all_accounts) == TestNumericConstants.COUNT_TWO

        # 12. Обрабатываем платеж на второй счет
        second_webhook = {
            "transaction_id": TestDomainIds.INTEGRATION_TX_002,
            "user_id": user_id,
            "account_id": second_account_id,
            "amount": str(TestMonetaryConstants.AMOUNT_75_00),
        }
        second_signature = compute_signature(
            account_id=second_webhook["account_id"],
            amount=Decimal(second_webhook["amount"]),
            transaction_id=second_webhook["transaction_id"],
            user_id=second_webhook["user_id"],
            secret_key=settings.webhook_secret_key,
        )
        second_webhook["signature"] = second_signature

        resp = await client.post(
            f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}",
            json=second_webhook,
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # 13. Проверяем, что оба счета имеют правильные балансы
        resp = await client.get(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
                user_id=user_id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        final_accounts = resp.json()

        # Находим счета по ID
        first_acc = next(acc for acc in final_accounts if acc["id"] == account_id)
        second_acc = next(
            acc for acc in final_accounts if acc["id"] == second_account_id
        )

        assert first_acc["balance"] == f"{TestMonetaryConstants.AMOUNT_150_00:.2f}"
        assert second_acc["balance"] == f"{TestMonetaryConstants.AMOUNT_75_00:.2f}"

        # 14. Проверяем общую историю платежей
        resp = await client.get(
            f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        all_payments = resp.json()
        assert len(all_payments) == TestNumericConstants.COUNT_TWO

        # Проверяем, что платежи идемпотентны
        resp = await client.post(
            f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}",
            json=webhook_payload,  # Повторяем первый платеж
        )
        assert resp.status_code == status.HTTP_409_CONFLICT
        assert TestErrorMessages.TRANSACTION_ALREADY_PROCESSED in resp.json()["detail"]

        # 15. Финальная проверка - админ видит всех пользователей
        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        all_users = resp.json()
        assert (
            len(all_users) >= TestNumericConstants.COUNT_TWO
        )  # Админ + созданный пользователь

        # Проверяем, что созданный пользователь в списке
        user_emails = [user["email"] for user in all_users]
        assert TestUserData.INTEGRATION_EMAIL in user_emails

    @pytest.mark.asyncio()
    async def test_multi_user_scenario_with_cross_operations(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        """Сценарий с несколькими пользователями и кросс-операциями."""
        settings = get_settings()
        users = CRUDUser()

        # Создаем администратора
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.MULTI_ADMIN_EMAIL,
                full_name=TestUserData.MULTI_ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            admin_token = make_token(admin.id)

        # Создаем нескольких пользователей
        user_emails = [
            TestUserData.MULTI_USER1_EMAIL,
            TestUserData.MULTI_USER2_EMAIL,
            TestUserData.MULTI_USER3_EMAIL,
        ]
        user_names = [
            TestUserData.MULTI_USER1_FULL_NAME,
            TestUserData.MULTI_USER2_FULL_NAME,
            TestUserData.MULTI_USER3_FULL_NAME,
        ]
        created_users = []

        for email, full_name in zip(user_emails, user_names):
            user_data = {
                "email": email,
                "full_name": full_name,
                "password": TestUserData.INTEGRATION_PASSWORD,
                "is_admin": False,
            }
            resp = await client.post(
                f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
                headers={
                    TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
                },
                json=user_data,
            )
            assert resp.status_code == status.HTTP_201_CREATED
            created_users.append(resp.json())

        # Создаем счета для всех пользователей
        account_ids = []
        for user in created_users:
            resp = await client.post(
                f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
                    user_id=user["id"]
                ),
                headers={
                    TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
                },
            )
            assert resp.status_code == status.HTTP_201_CREATED
            account_ids.append(resp.json()["id"])

        # Обрабатываем платежи для всех пользователей
        amounts = [
            TestMonetaryConstants.AMOUNT_100_00,
            TestMonetaryConstants.AMOUNT_200_00,
            TestMonetaryConstants.AMOUNT_200_00,
        ]

        for i, (user, account_id, amount) in enumerate(
            zip(created_users, account_ids, amounts)
        ):
            webhook_data = {
                "transaction_id": f"multi-tx-{i + 1:03d}",
                "user_id": user["id"],
                "account_id": account_id,
                "amount": str(amount),
            }
            signature = compute_signature(
                account_id=webhook_data["account_id"],
                amount=Decimal(webhook_data["amount"]),
                transaction_id=webhook_data["transaction_id"],
                user_id=webhook_data["user_id"],
                secret_key=settings.webhook_secret_key,
            )
            webhook_data["signature"] = signature

            resp = await client.post(
                f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}",
                json=webhook_data,
            )
            assert resp.status_code == status.HTTP_201_CREATED

        # Проверяем, что каждый пользователь видит только свои данные
        for i, user in enumerate(created_users):
            user_token = make_token(user["id"])

            # Проверяем счета
            resp = await client.get(
                f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
                    user_id=user["id"]
                ),
                headers={
                    TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
                },
            )
            assert resp.status_code == status.HTTP_200_OK
            user_accounts = resp.json()
            assert len(user_accounts) == TestNumericConstants.COUNT_SINGLE
            assert user_accounts[0]["balance"] == f"{amounts[i]:.2f}"

            # Проверяем платежи
            resp = await client.get(
                f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}",
                headers={
                    TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
                },
            )
            assert resp.status_code == status.HTTP_200_OK
            user_payments = resp.json()
            assert len(user_payments) == TestNumericConstants.COUNT_SINGLE
            assert user_payments[0]["amount"] == f"{amounts[i]:.2f}"

        # Проверяем, что обычные пользователи не могут видеть чужие данные
        user1_token = make_token(created_users[0]["id"])
        resp = await client.get(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
                user_id=created_users[1]["id"]
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user1_token}"
            },
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

        # Админ может видеть все данные
        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        all_users = resp.json()
        assert (
            len(all_users) >= len(user_emails) + TestNumericConstants.COUNT_SINGLE
        )  # + админ

    @pytest.mark.asyncio()
    async def test_error_scenarios_and_recovery(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        """Тестирование сценариев ошибок и восстановления."""
        users = CRUDUser()

        # Создаем администратора
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ERROR_ADMIN_EMAIL,
                full_name=TestUserData.ERROR_ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            admin_token = make_token(admin.id)

        # 1. Попытка создать пользователя с дублирующимся email
        user_data = {
            "email": TestUserData.DUPLICATE_EMAIL,
            "full_name": TestUserData.DUPLICATE_FULL_NAME,
            "password": TestUserData.INTEGRATION_PASSWORD,
        }

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
            json=user_data,
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # Повторная попытка создания с тем же email
        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
            json=user_data,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        # 2. Попытка создать счет для несуществующего пользователя
        resp = await client.post(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
                user_id=TestDomainIds.NONEXISTENT_USER_ID
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        # 3. Попытка webhook с неверной подписью
        webhook_data = {
            "transaction_id": TestDomainIds.INVALID_SIG_TX,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_ACCOUNT_ID,
            "amount": str(TestMonetaryConstants.AMOUNT_100_00),
            "signature": TestTransactionData.INVALID_SIGNATURE,
        }

        resp = await client.post(
            f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}",
            json=webhook_data,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        # 4. Попытка доступа к защищенным эндпоинтам без авторизации
        resp = await client.get(f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

        resp = await client.get(f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

        # 5. Попытка доступа с неверным токеном
        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: (
                    f"{TestAuthData.BEARER_PREFIX}{TestAuthData.INVALID_TOKEN}"
                )
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

        # 6. Попытка обычного пользователя получить доступ к админским эндпоинтам
        async with test_sessionmaker() as db:
            regular_user = await users.create(
                db,
                email=TestUserData.REGULAR_EMAIL,
                full_name=TestUserData.REGULAR_FULL_NAME,
                password=TestUserData.INTEGRATION_PASSWORD,
                is_admin=False,
            )
            await db.commit()
            user_token = make_token(regular_user.id)

        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{user_token}"
            },
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

        # 7. Восстановление после ошибок - создаем валидного пользователя
        valid_user_data = {
            "email": TestUserData.RECOVERY_EMAIL,
            "full_name": TestUserData.RECOVERY_FULL_NAME,
            "password": TestUserData.INTEGRATION_PASSWORD,
        }

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{admin_token}"
            },
            json=valid_user_data,
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # Проверяем, что пользователь создался корректно
        created_user = resp.json()
        assert created_user["email"] == valid_user_data["email"]
        assert created_user["full_name"] == valid_user_data["full_name"]
