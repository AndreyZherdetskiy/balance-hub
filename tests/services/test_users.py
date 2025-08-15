"""Тесты для UserService."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants import ErrorMessages
from app.core.errors import NotFoundError, ValidationError
from app.crud.users import CRUDUser
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.users import UserService
from app.validators.async_.users import UserAsyncValidator
from tests.constants import TestDomainIds, TestUserData


class TestUserService:
    """Тесты для UserService."""

    @pytest.fixture
    def user_service(self) -> UserService:
        """Создает экземпляр UserService."""
        users_crud = CRUDUser()
        return UserService(
            users_crud=users_crud, user_validator=UserAsyncValidator(users_crud)
        )

    @pytest.mark.asyncio()
    async def test_create_user_success(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест успешного создания пользователя."""
        async with test_sessionmaker() as db:
            user_data = UserCreate(
                email=TestUserData.NEW_USER_EMAIL,
                full_name=TestUserData.NEW_USER_FULL_NAME,
                password=TestUserData.NEW_PASS_123,
                is_admin=False,
            )

            result = await user_service.create_user(db, user_data)

            assert isinstance(result, User)
            assert result.email == user_data.email
            assert result.full_name == user_data.full_name
            assert result.is_admin == user_data.is_admin

    @pytest.mark.asyncio()
    async def test_create_user_duplicate_email_handling(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест обработки дублирования email при создании пользователя."""
        async with test_sessionmaker() as db:
            # Создаем первого пользователя
            user_data1 = UserCreate(
                email=TestUserData.EXISTING_EMAIL,
                full_name=TestUserData.FIRST_USER,
                password=TestUserData.PASS_123,
                is_admin=False,
            )
            await user_service.create_user(db, user_data1)

            # Пытаемся создать второго с тем же email
            user_data2 = UserCreate(
                email=TestUserData.EXISTING_EMAIL,
                full_name=TestUserData.SECOND_USER,
                password=TestUserData.PASS_456,
                is_admin=False,
            )

            with pytest.raises(
                ValidationError, match=ErrorMessages.EMAIL_ALREADY_EXISTS
            ):
                await user_service.create_user(db, user_data2)

    @pytest.mark.asyncio()
    async def test_get_all_users_success(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест успешного получения всех пользователей."""
        async with test_sessionmaker() as db:
            # Создаем несколько пользователей через сервис
            for email, full_name in zip(
                TestUserData.BATCH_EMAILS_ABC, TestUserData.BATCH_FULL_NAMES_ABC
            ):
                user_data = UserCreate(
                    email=email, full_name=full_name, password=TestUserData.PASS_123
                )
                await user_service.create_user(db, user_data)

            result = await user_service.get_all_users(db)

            assert len(result) >= 3
            assert all(isinstance(user, User) for user in result)

    @pytest.mark.asyncio()
    async def test_get_all_users_with_pagination(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест получения пользователей с пагинацией."""
        async with test_sessionmaker() as db:
            # Создаем 5 пользователей через сервис
            for email, full_name in zip(
                TestUserData.PAGINATED_EMAILS_ABCDE,
                TestUserData.PAGINATED_FULL_NAMES_ABCDE,
            ):
                user_data = UserCreate(
                    email=email, full_name=full_name, password=TestUserData.PASS_123
                )
                await user_service.create_user(db, user_data)

            # Тестируем пагинацию
            result = await user_service.get_all_users(db, limit=2, offset=0)
            assert len(result) == 2

            result = await user_service.get_all_users(db, limit=2, offset=2)
            assert len(result) == 2

            result = await user_service.get_all_users(db, limit=2, offset=4)
            assert len(result) == 1

    @pytest.mark.asyncio()
    async def test_get_user_by_id_success(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест успешного получения пользователя по ID."""
        async with test_sessionmaker() as db:
            # Создаем пользователя через сервис
            user_data = UserCreate(
                email=TestUserData.GETBYID_EMAIL,
                full_name=TestUserData.GETBYID_FULL_NAME,
                password=TestUserData.PASS_123,
            )
            user = await user_service.create_user(db, user_data)

            result = await user_service.get_user_by_id(db, user.id)

            assert isinstance(result, User)
            assert result.id == user.id
            assert result.email == user.email

    @pytest.mark.asyncio()
    async def test_get_user_by_id_not_found(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест получения несуществующего пользователя по ID."""
        async with test_sessionmaker() as db:
            with pytest.raises(NotFoundError, match=ErrorMessages.USER_NOT_FOUND):
                await user_service.get_user_by_id(db, TestDomainIds.NONEXISTENT_USER_ID)

    @pytest.mark.asyncio()
    async def test_update_user_success(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест успешного обновления пользователя."""
        async with test_sessionmaker() as db:
            # Создаем пользователя через сервис
            user_data = UserCreate(
                email=TestUserData.UPDATE_EMAIL,
                full_name=TestUserData.UPDATE_FULL_NAME,
                password=TestUserData.PASS_123,
            )
            user = await user_service.create_user(db, user_data)

            # Обновляем пользователя
            update_data = UserUpdate(full_name=TestUserData.UPDATED_NAME, is_admin=True)

            result = await user_service.update_user(db, user.id, update_data)

            assert result.full_name == TestUserData.UPDATED_NAME
            assert result.is_admin is True
            assert result.email == TestUserData.UPDATE_EMAIL  # Не изменился

    @pytest.mark.asyncio()
    async def test_update_user_email_change(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест обновления email пользователя."""
        async with test_sessionmaker() as db:
            # Создаем пользователя через сервис
            user_data = UserCreate(
                email=TestUserData.OLD_EMAIL,
                full_name=TestUserData.EMAIL_CHANGE_FULL_NAME,
                password=TestUserData.PASS_123,
            )
            user = await user_service.create_user(db, user_data)

            # Обновляем email
            update_data = UserUpdate(email=TestUserData.NEW_EMAIL)

            result = await user_service.update_user(db, user.id, update_data)

            assert result.email == TestUserData.NEW_EMAIL

    @pytest.mark.asyncio()
    async def test_update_user_email_uniqueness_validation(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест валидации уникальности email при обновлении."""
        async with test_sessionmaker() as db:
            # Создаем двух пользователей через сервис
            user_data1 = UserCreate(
                email=TestUserData.USER1_EMAIL,
                full_name=TestUserData.FIRST_USER,
                password=TestUserData.PASS_123,
            )
            user_data2 = UserCreate(
                email=TestUserData.USER2_EMAIL,
                full_name=TestUserData.SECOND_USER,
                password=TestUserData.PASS_123,
            )
            user1 = await user_service.create_user(db, user_data1)
            await user_service.create_user(db, user_data2)

            # Пытаемся обновить email первого пользователя на email второго
            update_data = UserUpdate(email=TestUserData.USER2_EMAIL)

            with pytest.raises(
                ValidationError, match=ErrorMessages.EMAIL_ALREADY_EXISTS
            ):
                await user_service.update_user(db, user1.id, update_data)

    @pytest.mark.asyncio()
    async def test_update_user_not_found(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест обновления несуществующего пользователя."""
        async with test_sessionmaker() as db:
            update_data = UserUpdate(full_name=TestUserData.UPDATED_NAME)

            with pytest.raises(NotFoundError, match=ErrorMessages.USER_NOT_FOUND):
                await user_service.update_user(db, 999, update_data)

    @pytest.mark.asyncio()
    async def test_update_user_partial_fields(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест обновления частичных полей пользователя."""
        async with test_sessionmaker() as db:
            # Создаем пользователя через сервис
            user_data = UserCreate(
                email=TestUserData.PARTIAL_EMAIL,
                full_name=TestUserData.PARTIAL_FULL_NAME,
                password=TestUserData.PASS_123,
                is_admin=False,
            )
            user = await user_service.create_user(db, user_data)

            # Обновляем только full_name
            update_data = UserUpdate(full_name=TestUserData.NEW_USER_FULL_NAME)

            result = await user_service.update_user(db, user.id, update_data)

            assert result.full_name == TestUserData.NEW_USER_FULL_NAME
            assert result.email == TestUserData.PARTIAL_EMAIL  # Не изменился
            assert result.is_admin is False  # Не изменился

    @pytest.mark.asyncio()
    async def test_delete_user_success(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест успешного удаления пользователя."""
        async with test_sessionmaker() as db:
            # Создаем пользователя через сервис
            user_data = UserCreate(
                email=TestUserData.DELETE_EMAIL,
                full_name=TestUserData.DELETE_FULL_NAME,
                password=TestUserData.PASS_123,
            )
            user = await user_service.create_user(db, user_data)

            # Удаляем пользователя
            await user_service.delete_user(db, user.id)

            # Проверяем, что пользователь удален
            users_crud = CRUDUser()
            deleted_user = await users_crud.get(db, user.id)
            assert deleted_user is None

    @pytest.mark.asyncio()
    async def test_delete_user_not_found(
        self,
        user_service: UserService,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест удаления несуществующего пользователя."""
        async with test_sessionmaker() as db:
            with pytest.raises(NotFoundError, match=ErrorMessages.USER_NOT_FOUND):
                await user_service.delete_user(db, TestDomainIds.NONEXISTENT_USER_ID)

    @pytest.mark.asyncio()
    async def test_user_service_dependency_injection(
        self,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест правильной работы dependency injection в UserService."""
        # Создаем мок CRUD объект
        mock_users_crud = CRUDUser()
        mock_validator = UserAsyncValidator(mock_users_crud)

        service = UserService(users_crud=mock_users_crud, user_validator=mock_validator)

        assert service.users_crud is mock_users_crud
        assert service.user_validator is mock_validator

    @pytest.mark.asyncio()
    async def test_user_service_without_validator(
        self,
        test_sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Тест UserService без валидатора."""
        users_crud = CRUDUser()
        service = UserService(users_crud=users_crud)

        # UserService автоматически создает валидатор, если не передан
        assert service.user_validator is not None
        assert isinstance(service.user_validator, UserAsyncValidator)

    @pytest.mark.asyncio()
    async def test_create_user_integrity_error_race(
        self,
        test_sessionmaker: async_sessionmaker[AsyncSession],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Гонка уникальности email.

        CRUD.create кидает IntegrityError → доменная ValidationError.
        """
        from app.schemas.user import UserCreate

        users_crud = CRUDUser()
        service = UserService(
            users_crud=users_crud, user_validator=UserAsyncValidator(users_crud)
        )

        async def fake_create(*args, **kwargs):  # type: ignore[no-untyped-def]
            raise IntegrityError("stmt", {}, Exception("duplicate"))

        monkeypatch.setattr(CRUDUser, "create", fake_create, raising=True)

        async with test_sessionmaker() as db:
            user_data = UserCreate(
                email=TestUserData.NEW_USER_EMAIL,
                full_name=TestUserData.NEW_USER_FULL_NAME,
                password=TestUserData.NEW_USER_PASSWORD,
                is_admin=False,
            )
            with pytest.raises(
                ValidationError, match=ErrorMessages.EMAIL_ALREADY_EXISTS
            ):
                await service.create_user(db, user_data)
