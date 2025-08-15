"""Тесты API аутентификации - все сценарии."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.crud.users import CRUDUser
from tests.constants import (
    TestAuthPaths,
    TestErrorMessages,
    TestUserData,
    TestAuthData,
    TestValidationData,
    TestAuthConstants,
)


class TestAuthApi:
    """Тесты аутентификации и авторизации."""

    @pytest.mark.asyncio()
    async def test_login_success(
        self, client: AsyncClient, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            await db.commit()

        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == TestAuthData.TOKEN_TYPE

    @pytest.mark.asyncio()
    async def test_login_invalid_credentials(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.WRONG_EMAIL,
                "password": TestUserData.WRONG_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert TestErrorMessages.INVALID_CREDENTIALS in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_users_me_invalid_token(self, client: AsyncClient) -> None:
        from tests.constants import TestUsersPaths

        me_path = f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}"
        resp = await client.get(
            me_path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{TestAuthData.INVALID_TOKEN}"
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_login_user_not_found(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.NONEXISTENT_EMAIL,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert TestErrorMessages.INVALID_CREDENTIALS in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_login_wrong_password(
        self, client: AsyncClient, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            await db.commit()

        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.WRONG_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert TestErrorMessages.INVALID_CREDENTIALS in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_login_empty_email(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestValidationData.EMPTY_STRING,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_login_invalid_email_format(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.INVALID_EMAIL_FORMAT,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_login_missing_fields(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(path, json={"email": TestUserData.USER_EMAIL})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        resp = await client.post(path, json={"password": TestUserData.USER_PASSWORD})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_login_with_extra_fields(
        self, client: AsyncClient, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            await db.commit()

        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.USER_PASSWORD,
                "extra_field": TestValidationData.EXTRA_FIELD,
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "access_token" in body and body["token_type"] == TestAuthData.TOKEN_TYPE

    @pytest.mark.asyncio()
    async def test_login_validation_error(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.INVALID_EMAIL_FORMAT,
                "password": TestUserData.TEST_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_login_none_values(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestValidationData.NONE_VALUE,
                "password": TestValidationData.NONE_VALUE,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_login_empty_json(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(path, json={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_login_no_json(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(path)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_login_generates_different_tokens(
        self, client: AsyncClient, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            await db.commit()

        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp1 = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp1.status_code == status.HTTP_200_OK
        token1 = resp1.json()["access_token"]

        import asyncio

        await asyncio.sleep(TestAuthConstants.TOKEN_GENERATION_DELAY)

        resp2 = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp2.status_code == status.HTTP_200_OK
        token2 = resp2.json()["access_token"]

        assert token1 != token2

    @pytest.mark.asyncio()
    async def test_login_case_sensitive_password(
        self, client: AsyncClient, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            await db.commit()

        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp1 = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp1.status_code == status.HTTP_200_OK

        resp2 = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.TEST_PASSWORD_ALT,
            },
        )
        assert resp2.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_login_email_case_sensitivity(
        self, client: AsyncClient, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            await db.commit()

        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp1 = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp1.status_code == status.HTTP_200_OK

        resp2 = await client.post(
            path,
            json={
                "email": TestUserData.TEST_EMAIL_UPPER,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp2.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_login_unicode_email(self, client: AsyncClient) -> None:
        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.UNICODE_EMAIL,
                "password": TestUserData.USER_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_login_unicode_password(
        self, client: AsyncClient, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        users = CRUDUser()
        async with test_sessionmaker() as db:
            await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.UNICODE_PASSWORD,
            )
            await db.commit()

        path = f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}"
        resp = await client.post(
            path,
            json={
                "email": TestUserData.USER_EMAIL,
                "password": TestUserData.UNICODE_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_200_OK
