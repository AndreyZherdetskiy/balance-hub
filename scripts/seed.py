"""Скрипт сидирования тестовых данных согласно ТЗ.

Создаёт:
- тестового пользователя
- счёт пользователя
- тестового администратора
"""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.account import Account
from app.models.user import User


async def seed() -> None:
    """Сидирование тестовых данных."""

    async with AsyncSessionLocal() as db:  # type: AsyncSession
        # создаём тестового пользователя
        res = await db.execute(
            select(User).where(
                User.email == os.getenv("DEFAULT_USER_EMAIL", "user@example.com")
            )
        )
        user = res.scalar_one_or_none()
        if user is None:
            user = User(
                email=os.getenv("DEFAULT_USER_EMAIL", "user@example.com"),
                full_name=os.getenv("DEFAULT_USER_FULL_NAME", "Test User"),
                hashed_password=hash_password(
                    os.getenv("DEFAULT_USER_PASSWORD", "Password123!")
                ),
                is_admin=False,
            )
            db.add(user)
            await db.flush()

        # создаём счёт пользователя
        res = await db.execute(select(Account).where(Account.user_id == user.id))
        account = res.scalar_one_or_none()
        if account is None:
            account = Account(user_id=user.id, balance=Decimal("0.00"))
            db.add(account)

        # создаём тестового администратора
        res = await db.execute(
            select(User).where(
                User.email == os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
            )
        )
        admin = res.scalar_one_or_none()
        if admin is None:
            admin = User(
                email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com"),
                full_name=os.getenv("DEFAULT_ADMIN_FULL_NAME", "Admin User"),
                hashed_password=hash_password(
                    os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin123!")
                ),
                is_admin=True,
            )
            db.add(admin)

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
