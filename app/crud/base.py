"""Базовый класс CRUD для асинхронной работы с моделями."""

from __future__ import annotations

from typing import Generic, Iterable, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


ModelT = TypeVar('ModelT')


class CRUDBase(Generic[ModelT]):
    """Базовый CRUD для ORM-модели.

    Args:
        model (type[ModelT]): Класс ORM-модели.
    """

    def __init__(self, model: type[ModelT]) -> None:
        """Инициализирует базовый CRUD-класс.

        Args:
            model (type[ModelT]): Класс ORM-модели.
        """
        self.model = model

    async def get(self, db: AsyncSession, obj_id: int) -> ModelT | None:
        """Возвращает объект по идентификатору.

        Args:
            db (AsyncSession): Сессия БД.
            obj_id (int): Идентификатор объекта.

        Returns:
            ModelT | None: Найденный объект или None.
        """
        result = await db.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalar_one_or_none()

    async def list_all(self, db: AsyncSession) -> Iterable[ModelT]:
        """Возвращает все объекты модели.

        Args:
            db (AsyncSession): Сессия БД.

        Returns:
            Iterable[ModelT]: Список объектов модели.
        """
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def delete(self, db: AsyncSession, obj: ModelT) -> None:
        """Удаляет объект.

        Args:
            db (AsyncSession): Сессия БД.
            obj (ModelT): Экземпляр модели для удаления.
        """
        await db.delete(obj)
        await db.flush()
