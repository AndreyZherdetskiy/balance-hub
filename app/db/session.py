"""Инициализация асинхронного движка БД и фабрики сессий."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


settings = get_settings()
engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию БД на время обработки запроса.

    Yields:
        AsyncSession: Живую сессию SQLAlchemy для выполнения операций.
    """
    async with AsyncSessionLocal() as session:
        yield session
