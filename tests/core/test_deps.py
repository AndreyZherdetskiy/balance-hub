"""Тесты для модуля зависимостей приложения."""

from __future__ import annotations

import pytest
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.core.deps import (
    get_current_admin,
    get_current_user,
    require_self_or_admin_user,
)
from app.core.security import create_access_token
from app.crud.users import CRUDUser
from app.models.user import User
from tests.constants import (
    TestAuthConstants,
    TestAuthData,
    TestDomainIds,
    TestErrorMessages,
    TestUserData,
    TestValidationData,
)


class TestDeps:
    """Тесты зависимостей core слоя."""

    @pytest.mark.asyncio()
    async def test_get_current_user_invalid_token_format(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Токен в неверном формате должен дать 401."""
        async with test_sessionmaker() as db:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db, TestAuthData.INVALID_FORMAT, get_settings())
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert TestErrorMessages.NOT_AUTHENTICATED in exc_info.value.detail

    @pytest.mark.asyncio()
    async def test_get_current_user_missing_subject(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Токен без subject должен дать 401."""
        settings = get_settings()
        invalid_token = jwt.encode(
            {"exp": TestAuthConstants.LONG_FUTURE_EXP_TS},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )

        async with test_sessionmaker() as db:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db, invalid_token, settings)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_get_current_user_invalid_subject_format(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Нечисловой subject должен дать 401."""
        settings = get_settings()
        invalid_token = jwt.encode(
            {
                "sub": TestValidationData.INVALID_SUBJECT_STR,
                "exp": TestAuthConstants.LONG_FUTURE_EXP_TS,
            },
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )

        async with test_sessionmaker() as db:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db, invalid_token, settings)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_get_current_user_nonexistent_user(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Несуществующий пользователь должен дать 401."""
        settings = get_settings()
        token = create_access_token(
            TestDomainIds.NONEXISTENT_USER_ID,
            settings.jwt_secret,
            settings.jwt_algorithm,
            settings.jwt_expires_minutes,
        )

        async with test_sessionmaker() as db:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db, token, settings)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio()
    async def test_get_current_admin_success(
        self, test_sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        """У администратора доступ разрешён."""
        users = CRUDUser()
        async with test_sessionmaker() as db:
            admin = await users.create(
                db,
                email=TestUserData.ADMIN_EMAIL,
                full_name=TestUserData.ADMIN_FULL_NAME,
                password=TestUserData.ADMIN_PASSWORD,
                is_admin=True,
            )

        result = await get_current_admin(admin)
        assert result == admin

    @pytest.mark.asyncio()
    async def test_get_current_admin_not_admin(self) -> None:
        """У не-админа доступ запрещён."""
        user = User(
            id=TestDomainIds.TEST_USER_ID,
            email=TestUserData.USER_EMAIL,
            full_name=TestUserData.USER_FULL_NAME,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
            is_admin=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert TestErrorMessages.FORBIDDEN in exc_info.value.detail

    def test_require_self_or_admin_user_owner_access(self) -> None:
        """Владелец имеет доступ к своему ресурсу."""
        user = User(
            id=TestDomainIds.TEST_USER_ID,
            email=TestUserData.USER_EMAIL,
            full_name=TestUserData.USER_FULL_NAME,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
            is_admin=False,
        )

        require_self_or_admin_user(TestDomainIds.TEST_USER_ID, user)

    def test_require_self_or_admin_user_admin_access(self) -> None:
        """Администратор имеет доступ к чужому ресурсу."""
        admin = User(
            id=TestDomainIds.TEST_USER_ID,
            email=TestUserData.ADMIN_EMAIL,
            full_name=TestUserData.ADMIN_FULL_NAME,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
            is_admin=True,
        )

        require_self_or_admin_user(TestDomainIds.NONEXISTENT_USER_ID, admin)

    def test_require_self_or_admin_user_forbidden(self) -> None:
        """Обычному пользователю запрещён доступ к чужому ресурсу."""
        user = User(
            id=TestDomainIds.TEST_USER_ID,
            email=TestUserData.USER_EMAIL,
            full_name=TestUserData.USER_FULL_NAME,
            hashed_password=TestUserData.TEST_HASHED_PASSWORD,
            is_admin=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            require_self_or_admin_user(TestDomainIds.NONEXISTENT_USER_ID, user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert TestErrorMessages.ACCESS_DENIED in exc_info.value.detail
