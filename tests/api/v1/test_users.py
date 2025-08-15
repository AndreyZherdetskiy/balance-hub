"""Тесты API пользователей - все сценарии."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.crud.users import CRUDUser
from tests.constants import (
    TestDomainIds,
    TestErrorMessages,
    TestUserData,
    TestAuthData,
    TestNumericConstants,
    TestValidationData,
)


class TestUsersApi:
    """Тесты эндпоинтов пользователей."""

    @pytest.mark.asyncio()
    async def test_users_me_success(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.ME_USER_EMAIL,
                full_name=TestUserData.ME_USER_FULL_NAME,
                password=TestUserData.ME_USER_PASSWORD,
            )
            await db.commit()
            token = make_token(user.id)

        path = f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}"
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["email"] == TestUserData.ME_USER_EMAIL
        assert body["full_name"] == TestUserData.ME_USER_FULL_NAME
        assert "id" in body

    @pytest.mark.asyncio()
    async def test_users_me_with_valid_token(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.ME_USER_EMAIL,
                full_name=TestUserData.ME_USER_FULL_NAME,
                password=TestUserData.ME_USER_PASSWORD,
            )
            await db.commit()
            token = make_token(user.id)

        path = f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}"
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["email"] == TestUserData.ME_USER_EMAIL
        assert body["full_name"] == TestUserData.ME_USER_FULL_NAME
        assert body["is_admin"] is False
        assert "id" in body

    @pytest.mark.asyncio()
    async def test_admin_users_crud_full_flow(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={
                "email": TestUserData.JOHN_EMAIL,
                "full_name": TestUserData.JOHN_FULL_NAME,
                "password": TestUserData.JOHN_PASSWORD,
                "is_admin": False,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED
        created = resp.json()

        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        assert any(u["email"] == TestUserData.JOHN_EMAIL for u in resp.json())

        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=created["id"]
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK

        resp = await client.patch(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=created["id"]
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={"full_name": TestUserData.JOHNNY_NAME},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["full_name"] == TestUserData.JOHNNY_NAME

        resp = await client.delete(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=created["id"]
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio()
    async def test_admin_create_user_success(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            token = make_token(admin.id)
        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={
                "email": TestUserData.NEW_USER_EMAIL,
                "full_name": TestUserData.NEW_USER_FULL_NAME,
                "password": TestUserData.NEW_USER_PASSWORD,
                "is_admin": False,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED
        body = resp.json()
        assert body["email"] == TestUserData.NEW_USER_EMAIL
        assert body["full_name"] == TestUserData.NEW_USER_FULL_NAME
        assert "id" in body

    @pytest.mark.asyncio()
    async def test_admin_list_users_success(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await users.create(
                db,
                email=TestUserData.USER1_EMAIL,
                full_name=TestUserData.USER1_FULL_NAME,
                password=TestUserData.USER1_PASSWORD,
            )
            await db.commit()

        token = make_token(admin.id)
        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= TestNumericConstants.COUNT_TWO

    @pytest.mark.asyncio()
    async def test_admin_get_user_not_found(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.get(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=TestDomainIds.NONEXISTENT_USER_ID
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert TestErrorMessages.USER_NOT_FOUND in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_admin_update_user_not_found(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.patch(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=TestDomainIds.NONEXISTENT_USER_ID
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={"full_name": TestUserData.UPDATED_NAME},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert TestErrorMessages.USER_NOT_FOUND in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_admin_delete_user_not_found(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.delete(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=TestDomainIds.NONEXISTENT_USER_ID
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert TestErrorMessages.USER_NOT_FOUND in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_admin_create_user_duplicate_email(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await users.create(
                db,
                email=TestUserData.EXISTING_EMAIL,
                full_name=TestUserData.EXISTING_FULL_NAME,
                password=TestUserData.EXISTING_PASSWORD,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={
                "email": TestUserData.EXISTING_EMAIL,
                "full_name": TestUserData.TEST_NAME_DUPLICATE,
                "password": TestUserData.EXISTING_PASSWORD,
                "is_admin": False,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert TestErrorMessages.EMAIL_ALREADY_EXISTS in resp.json()["detail"]

    @pytest.mark.asyncio()
    async def test_admin_create_user_invalid_password(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={
                "email": TestUserData.NEW_USER_EMAIL,
                "full_name": TestUserData.NEW_USER_FULL_NAME,
                "password": TestUserData.SHORT_PASSWORD,
                "is_admin": False,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_non_admin_access_forbidden_all_endpoints(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            user = await users.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            await db.commit()
            token = make_token(user.id)

        admin_endpoints = [
            ("GET", f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}"),
            ("POST", f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}"),
            (
                "GET",
                f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                    user_id=TestDomainIds.TEST_USER_ID
                ),
            ),
            (
                "PATCH",
                f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                    user_id=TestDomainIds.TEST_USER_ID
                ),
            ),
            (
                "DELETE",
                f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                    user_id=TestDomainIds.TEST_USER_ID
                ),
            ),
        ]

        for method, endpoint in admin_endpoints:
            resp = await client.request(
                method,
                endpoint,
                headers={
                    TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
                },
                json={"full_name": TestValidationData.TEST_FULL_NAME}
                if method in ["POST", "PATCH"]
                else None,
            )
            assert resp.status_code == status.HTTP_403_FORBIDDEN, (
                f"Endpoint {method} {endpoint} should return 403"
            )

    @pytest.mark.asyncio()
    async def test_users_me_unauthorized(self, client: AsyncClient) -> None:
        from tests.constants import TestUsersPaths

        path = f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}"
        resp = await client.get(path)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_admin_endpoints_require_auth(self, client: AsyncClient) -> None:
        from tests.constants import TestUsersPaths

        endpoints = [
            ("GET", f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}"),
            ("POST", f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}"),
            (
                "GET",
                f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                    user_id=TestDomainIds.TEST_USER_ID
                ),
            ),
            (
                "PATCH",
                f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                    user_id=TestDomainIds.TEST_USER_ID
                ),
            ),
            (
                "DELETE",
                f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                    user_id=TestDomainIds.TEST_USER_ID
                ),
            ),
        ]

        for method, endpoint in endpoints:
            resp = await client.request(
                method,
                endpoint,
                json={"full_name": TestValidationData.TEST_FULL_NAME}
                if method in ["POST", "PATCH"]
                else None,
            )
            assert resp.status_code == status.HTTP_401_UNAUTHORIZED, (
                f"Endpoint {method} {endpoint} should require auth"
            )

    @pytest.mark.asyncio()
    async def test_users_me_invalid_token_format(self, client: AsyncClient) -> None:
        from tests.constants import TestUsersPaths

        path = f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}"
        resp = await client.get(
            path,
            headers={TestAuthData.AUTHORIZATION_HEADER: TestAuthData.INVALID_FORMAT},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_users_me_expired_token(self, client: AsyncClient) -> None:
        from tests.constants import TestUsersPaths

        path = f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}"
        resp = await client.get(
            path,
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{TestAuthData.EXPIRED_TOKEN}"
            },
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_admin_create_user_invalid_email(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={
                "email": TestUserData.INVALID_EMAIL_FORMAT,
                "full_name": TestValidationData.TEST_USER_FULL_NAME,
                "password": TestUserData.NEW_USER_PASSWORD,
                "is_admin": False,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_admin_create_user_missing_fields(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={
                "full_name": TestValidationData.TEST_USER_FULL_NAME,
                "password": TestUserData.NEW_USER_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={
                "email": TestUserData.TEST_EMAIL_GENERIC,
                "password": TestUserData.NEW_USER_PASSWORD,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        resp = await client.post(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}",
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={
                "email": TestUserData.TEST_EMAIL_GENERIC,
                "full_name": TestValidationData.TEST_USER_FULL_NAME,
            },
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio()
    async def test_admin_update_user_partial_fields(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

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
                full_name=TestUserData.ORIGINAL_NAME,
                password=TestUserData.USER_PASSWORD,
            )
            await db.commit()
            token = make_token(admin.id)

        resp = await client.patch(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=user.id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={"full_name": TestUserData.UPDATED_NAME},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["full_name"] == TestUserData.UPDATED_NAME
        assert resp.json()["email"] == TestUserData.USER_EMAIL

    @pytest.mark.asyncio()
    async def test_admin_update_user_empty_json(
        self,
        client: AsyncClient,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        make_token: callable,  # type: ignore[type-arg]
    ) -> None:
        from tests.constants import TestUsersPaths

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
            await db.commit()
            token = make_token(admin.id)

        resp = await client.patch(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USER_ID}".format(
                user_id=user.id
            ),
            headers={
                TestAuthData.AUTHORIZATION_HEADER: f"{TestAuthData.BEARER_PREFIX}{token}"
            },
            json={},
        )
        assert resp.status_code == status.HTTP_200_OK
