"""Security utilities: password hashing and JWT tokens."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext


password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    """Hash plain password using bcrypt."""
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | int, secret: str, algorithm: str, expires_minutes: int) -> str:
    """Create a JWT access token for a given subject."""
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    to_encode: Dict[str, Any] = {"sub": str(subject), "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    return jwt.encode(to_encode, secret, algorithm=algorithm)
