"""Unit-тесты для модуля безопасности (`app.core.security`)."""

from __future__ import annotations

from app.core.security import create_access_token, hash_password, verify_password
from tests.constants import TestAuthConstants, TestDomainIds, TestUserData


class TestSecurity:
    """Тесты хеширования паролей и токенов."""

    def test_password_hash_and_verify(self) -> None:
        """Тест хеширования и проверки паролей."""
        plain = TestUserData.TEST_PASSWORD_STRONG
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed) is True
        assert verify_password(TestUserData.WRONG_PASSWORD_SHORT, hashed) is False

    def test_create_access_token_smoke(self) -> None:
        """Тест создания access токена."""
        token = create_access_token(
            subject=TestDomainIds.TEST_USER_ID,
            secret=TestUserData.TEST_SECRET,
            algorithm=TestUserData.TEST_JWT_ALGORITHM,
            expires_minutes=TestAuthConstants.JWT_EXPIRES_MINUTES_SHORT,
        )
        assert (
            isinstance(token, str) and len(token) > TestAuthConstants.MIN_TOKEN_LENGTH
        )
