"""User service: CRUD operations."""
from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User


async def create_user(db: AsyncSession, email: str, full_name: str, password: str, is_admin: bool = False) -> User:
    """Create a new user."""
    user = User(email=email, full_name=full_name, hashed_password=hash_password(password), is_admin=is_admin)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """Get a user by id."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession) -> Iterable[User]:
    """List all users."""
    result = await db.execute(select(User))
    return result.scalars().all()


async def update_user(
    db: AsyncSession,
    user: User,
    *,
    email: str | None = None,
    full_name: str | None = None,
    password: str | None = None,
    is_admin: bool | None = None,
) -> User:
    """Update an existing user."""
    if email is not None:
        user.email = email
    if full_name is not None:
        user.full_name = full_name
    if password is not None:
        user.hashed_password = hash_password(password)
    if is_admin is not None:
        user.is_admin = is_admin
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    """Delete a user."""
    await db.delete(user)
    await db.commit()
