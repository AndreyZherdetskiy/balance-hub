"""Утилиты безопасности: хеширование паролей и JWT токены."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Вычисляет bcrypt-хеш пароля.

    Args:
        password: Открытый пароль.

    Returns:
        str: Хеш пароля.
    """
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его bcrypt-хешу.

    Args:
        plain_password: Открытый пароль.
        hashed_password: Ранее сохранённый хеш.

    Returns:
        bool: True если пароль корректен.
    """
    return password_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | int, secret: str, algorithm: str, expires_minutes: int
) -> str:
    """Создаёт JWT-токен доступа.

    Args:
        subject (str | int): Идентификатор пользователя (claim `sub`).
        secret (str): Секретная строка для подписи.
        algorithm (str): Алгоритм подписи.
        expires_minutes (int): Время жизни токена в минутах.

    Returns:
        str: Подписанный JWT.
    """
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, secret, algorithm=algorithm)
