"""Тесты CRUD пользователей - все сценарии."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.crud.users import CRUDUser
from tests.constants import (
    TestDomainIds,
    TestNumericConstants,
    TestUserData,
    TestValidationData,
)


class TestUsersCRUD:
    """Базовые и расширенные CRUD-сценарии для пользователей."""

    @pytest.mark.asyncio()
    async def test_user_crud_create_get_update_list_delete(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест полного CRUD цикла для пользователей."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            user = await crud.create(
                db,
                email=TestUserData.JOHN_EMAIL,
                full_name=TestUserData.JOHN_FULL_NAME,
                password=TestUserData.TEST_PASSWORD_STRONG,
                is_admin=False,
            )
            assert user.id is not None

            got = await crud.get(db, user.id)
            assert got is not None and got.email == TestUserData.JOHN_EMAIL

            updated = await crud.update(db, got, full_name=TestUserData.JOHNNY_NAME)  # type: ignore[arg-type]
            assert updated.full_name == TestUserData.JOHNNY_NAME

            all_users = await crud.list_all(db)
            assert len(list(all_users)) == TestNumericConstants.COUNT_SINGLE

            await crud.delete(db, updated)
            assert await crud.get(db, user.id) is None

    @pytest.mark.asyncio()
    async def test_user_update_partial_fields(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест частичного обновления полей пользователя."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            user = await crud.create(
                db,
                email=TestUserData.JOHN_EMAIL,
                full_name=TestUserData.JOHN_FULL_NAME,
                password=TestUserData.TEST_PASSWORD_STRONG,
                is_admin=False,
            )
            original_email = user.email
            original_password = user.hashed_password

            updated = await crud.update(db, user, full_name=TestUserData.UPDATED_NAME)
            assert updated.full_name == TestUserData.UPDATED_NAME
            assert updated.email == original_email
            assert updated.hashed_password == original_password
            assert updated.is_admin is False

            updated = await crud.update(db, user, is_admin=True)
            assert updated.is_admin is True
            assert updated.full_name == TestUserData.UPDATED_NAME

            updated = await crud.update(
                db, user, password=TestUserData.NEW_USER_PASSWORD
            )
            assert updated.hashed_password != original_password
            assert updated.full_name == TestUserData.UPDATED_NAME
            assert updated.is_admin is True

            updated = await crud.update(db, user, email=TestUserData.JOHNNY_EMAIL)
            assert updated.email == TestUserData.JOHNNY_EMAIL

    @pytest.mark.asyncio()
    async def test_user_get_by_email_not_found(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест получения пользователя по несуществующему email."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            user = await crud.get_by_email(db, TestUserData.NONEXISTENT_EMAIL)
            assert user is None

    @pytest.mark.asyncio()
    async def test_user_get_by_email_exists(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест получения пользователя по существующему email."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            created_user = await crud.create(
                db,
                email=TestUserData.EXISTING_EMAIL,
                full_name=TestUserData.EXISTING_FULL_NAME,
                password=TestUserData.EXISTING_PASSWORD,
            )

            found_user = await crud.get_by_email(db, TestUserData.EXISTING_EMAIL)
            assert found_user is not None
            assert found_user.id == created_user.id
            assert found_user.email == TestUserData.EXISTING_EMAIL

    @pytest.mark.asyncio()
    async def test_user_get_by_email_case_sensitivity(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест чувствительности к регистру при поиске по email."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            await crud.create(
                db,
                email=TestUserData.TEST_EMAIL_GENERIC,
                full_name=TestValidationData.TEST_USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
            )

            user_exact = await crud.get_by_email(db, TestUserData.TEST_EMAIL_GENERIC)
            assert user_exact is not None

            user_upper = await crud.get_by_email(db, TestUserData.TEST_EMAIL_UPPER)
            assert user_upper is None

    @pytest.mark.asyncio()
    async def test_user_list_all_empty(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест получения пустого списка пользователей."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            users = await crud.list_all(db)
            users_list = list(users)
            assert len(users_list) == TestNumericConstants.COUNT_EMPTY

    @pytest.mark.asyncio()
    async def test_user_list_all_multiple_users(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест получения списка нескольких пользователей."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            await crud.create(
                db,
                email=TestUserData.USER1_EMAIL,
                full_name=TestUserData.USER1_FULL_NAME,
                password=TestUserData.USER1_PASSWORD,
            )
            await crud.create(
                db,
                email=TestUserData.USER2_EMAIL,
                full_name=TestUserData.USER2_FULL_NAME,
                password=TestUserData.USER2_PASSWORD,
            )
            await crud.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )

            users = await crud.list_all(db)
            users_list = list(users)
            assert len(users_list) == TestNumericConstants.COUNT_THREE

            emails = [user.email for user in users_list]
            assert len(set(emails)) == TestNumericConstants.COUNT_THREE

    @pytest.mark.asyncio()
    async def test_user_create_duplicate_email(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания пользователя с дублирующимся email."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            await crud.create(
                db,
                email=TestUserData.EXISTING_EMAIL,
                full_name=TestUserData.EXISTING_FULL_NAME,
                password=TestUserData.EXISTING_PASSWORD,
            )

            with pytest.raises(Exception):
                await crud.create(
                    db,
                    email=TestUserData.EXISTING_EMAIL,
                    full_name=TestUserData.TEST_NAME_DUPLICATE,
                    password=TestUserData.EXISTING_PASSWORD,
                )

    @pytest.mark.asyncio()
    async def test_user_get_nonexistent_id(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест получения пользователя по несуществующему ID."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            user = await crud.get(db, TestDomainIds.NONEXISTENT_USER_ID)
            assert user is None

    @pytest.mark.asyncio()
    async def test_user_update_nonexistent_user(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест обновления несуществующего пользователя."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            from app.models.user import User

            fake_user = User(
                id=TestDomainIds.NONEXISTENT_USER_ID,
                email=TestUserData.NONEXISTENT_EMAIL,
                full_name=TestUserData.ORIGINAL_NAME,
                hashed_password=TestUserData.TEST_HASHED_PASSWORD,
            )

            await crud.update(db, fake_user, full_name=TestUserData.UPDATED_NAME)
            found = await crud.get_by_email(db, TestUserData.NONEXISTENT_EMAIL)
            assert found is None

    @pytest.mark.asyncio()
    async def test_user_delete_nonexistent_user(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест удаления несуществующего пользователя."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            real_user = await crud.create(
                db,
                email=TestUserData.NEW_USER_EMAIL,
                full_name=TestUserData.NEW_USER_FULL_NAME,
                password=TestUserData.NEW_USER_PASSWORD,
            )
            await crud.delete(db, real_user)

    @pytest.mark.asyncio()
    async def test_user_create_empty_password(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания пользователя с пустым паролем."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            user = await crud.create(
                db,
                email=TestUserData.TEST_EMAIL_GENERIC,
                full_name=TestValidationData.TEST_USER_FULL_NAME,
                password=TestValidationData.EMPTY_STRING,
            )
            assert user.hashed_password != TestValidationData.EMPTY_STRING
            assert len(user.hashed_password) > 10

    @pytest.mark.asyncio()
    async def test_user_update_password_hashing(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест хеширования пароля при обновлении."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            user = await crud.create(
                db,
                email=TestUserData.EXISTING_EMAIL,
                full_name=TestUserData.EXISTING_FULL_NAME,
                password=TestUserData.TEST_PASSWORD_STRONG,
            )
            original_hash = user.hashed_password

            updated = await crud.update(
                db, user, password=TestUserData.TEST_PASSWORD_NEW
            )

            assert updated.hashed_password != original_hash
            assert updated.hashed_password != TestUserData.TEST_PASSWORD_NEW

    @pytest.mark.asyncio()
    async def test_user_create_with_unicode(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания пользователя с Unicode данными."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            user = await crud.create(
                db,
                email=TestUserData.UNICODE_EMAIL,
                full_name=TestUserData.UNICODE_FULL_NAME,
                password=TestUserData.UNICODE_PASSWORD,
            )

            assert user.email == TestUserData.UNICODE_EMAIL
            assert user.full_name == TestUserData.UNICODE_FULL_NAME

            found = await crud.get_by_email(db, TestUserData.UNICODE_EMAIL)
            assert found is not None
            assert found.id == user.id

    @pytest.mark.asyncio()
    async def test_user_create_with_long_data(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания пользователя с длинными данными."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            long_name = TestUserData.LONG_NAME_200_A
            long_email = TestUserData.LONG_EMAIL_LOCAL_A100_EXAMPLE_COM

            user = await crud.create(
                db,
                email=long_email,
                full_name=long_name,
                password=TestUserData.TEST_PASSWORD_STRONG,
            )

            assert user.email == long_email
            assert user.full_name == long_name

    @pytest.mark.asyncio()
    async def test_user_create_admin(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест создания пользователя-администратора."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            admin = await crud.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )

            assert admin.is_admin is True

            found = await crud.get(db, admin.id)
            assert found is not None
            assert found.is_admin is True

    @pytest.mark.asyncio()
    async def test_user_promote_to_admin(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Тест повышения пользователя до администратора."""
        crud = CRUDUser()

        async with test_sessionmaker() as db:
            user = await crud.create(
                db,
                email=TestUserData.USER_EMAIL,
                full_name=TestUserData.USER_FULL_NAME,
                password=TestUserData.USER_PASSWORD,
                is_admin=False,
            )
            assert user.is_admin is False

            admin = await crud.update(db, user, is_admin=True)
            assert admin.is_admin is True

            found = await crud.get(db, user.id)
            assert found is not None
            assert found.is_admin is True
