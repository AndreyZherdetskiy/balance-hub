"""Тесты API счетов - все сценарии."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.crud.users import CRUDUser
from tests.constants import (
    TestAccountsPaths,
    TestErrorMessages,
    TestUserData,
    TestAuthData,
    TestPaginationParams,
    TestDomainIds,
)


class TestAccountsApi:
    """Тесты эндпоинтов счетов."""

    @pytest.mark.asyncio()
    async def test_list_user_accounts_owner_access(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.OWNER_EMAIL,
                full_name=TestUserData.OWNER_FULL_NAME,
                password=TestUserData.OWNER_PASSWORD,
            )
            user_id = user.id
            await db.commit()

        token = make_token(user_id)
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=user_id
        )
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio()
    async def test_admin_create_account_success(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            user = await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            admin_id = admin.id
            user_id = user.id
            await db.commit()

        token = make_token(admin_id)
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
            user_id=user_id
        )
        resp = await client.post(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED
        body = resp.json()
        assert body["user_id"] == user_id
        assert "id" in body
        assert "balance" in body

    @pytest.mark.asyncio()
    async def test_list_user_accounts_forbidden_access(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            user1 = await users.create(
                db,
                email=TestUserData.USER1_EMAIL,
                full_name=TestUserData.USER1_FULL_NAME,
                password=TestUserData.USER1_PASSWORD,
            )
            user2 = await users.create(
                db,
                email=TestUserData.USER2_EMAIL,
                full_name=TestUserData.USER2_FULL_NAME,
                password=TestUserData.USER2_PASSWORD,
            )
            user1_id = user1.id
            user2_id = user2.id
            await db.commit()

        token = make_token(user1_id)
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=user2_id
        )
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio()
    async def test_list_accounts_access_denied_non_owner(
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
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=TestDomainIds.NONEXISTENT_USER_ID
        )
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert TestErrorMessages.ACCESS_DENIED in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_list_accounts_pagination_valid(
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
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=user_id
        )
        resp = await client.get(
            f"{path}?limit={TestPaginationParams.DEFAULT_LIMIT}&offset={TestPaginationParams.DEFAULT_OFFSET}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio()
    async def test_list_accounts_pagination_invalid_limits(
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
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=user_id
        )
        resp = await client.get(
            f"{path}?limit={TestPaginationParams.INVALID_LIMIT_NEGATIVE}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        resp = await client.get(
            f"{path}?limit={TestPaginationParams.INVALID_LIMIT_TOO_LARGE}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        resp = await client.get(
            f"{path}?offset={TestPaginationParams.INVALID_OFFSET_NEGATIVE}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_admin_create_account_user_not_found(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            admin_id = admin.id
            await db.commit()

        token = make_token(admin_id)
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
            user_id=TestDomainIds.NONEXISTENT_USER_ID
        )
        resp = await client.post(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert TestErrorMessages.USER_NOT_FOUND == resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_non_admin_create_account_forbidden(
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
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
            user_id=user_id
        )
        resp = await client.post(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio()
    async def test_list_accounts_without_auth(self, client: AsyncClient) -> None:
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=TestDomainIds.TEST_USER_ID
        )
        resp = await client.get(path)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_create_account_without_auth(self, client: AsyncClient) -> None:
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
            user_id=TestDomainIds.TEST_USER_ID
        )
        resp = await client.post(path)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_list_accounts_invalid_token(self, client: AsyncClient) -> None:
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=TestDomainIds.TEST_USER_ID
        )
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{TestAuthData.INVALID_TOKEN}"
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_create_account_invalid_token(self, client: AsyncClient) -> None:
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}".format(
            user_id=TestDomainIds.TEST_USER_ID
        )
        resp = await client.post(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{TestAuthData.INVALID_TOKEN}"
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_list_accounts_malformed_auth_header(
        self, client: AsyncClient
    ) -> None:
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=TestDomainIds.TEST_USER_ID
        )
        resp = await client.get(
            path,
            headers={TestAuthData.AUTHORIZATION_HEADER: TestAuthData.MALFORMED_AUTH},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_list_accounts_missing_bearer_prefix(
        self, client: AsyncClient
    ) -> None:
        path = f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}".format(
            user_id=TestDomainIds.TEST_USER_ID
        )
        resp = await client.get(
            path,
            headers={TestAuthData.AUTHORIZATION_HEADER: TestAuthData.MISSING_BEARER},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
