"""Authentication service functions."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.models.user import User


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate user by email and password."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def login(db: AsyncSession, email: str, password: str) -> str:
    """Return JWT token if credentials are valid."""
    settings = get_settings()
    user = await authenticate_user(db, email, password)
    if not user:
        raise ValueError('Invalid credentials')
    return create_access_token(user.id, settings.jwt_secret, settings.jwt_algorithm, settings.jwt_expires_minutes)
