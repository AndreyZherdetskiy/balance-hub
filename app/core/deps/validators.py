"""DI провайдеры для асинхронных валидаторов."""

from __future__ import annotations

from fastapi import Depends

from app.core.deps.crud import get_user_crud
from app.crud.users import CRUDUser
from app.validators.async_ import UserAsyncValidator


def get_user_async_validator(
    users_crud: CRUDUser = Depends(get_user_crud),
) -> UserAsyncValidator:
    """Возвращает асинхронный валидатор пользователей.

    Args:
        users_crud (CRUDUser): CRUD-уровень для пользователей.

    Returns:
        UserAsyncValidator: Валидатор для асинхронных проверок инвариантов.
    """
    return UserAsyncValidator(users_crud)
