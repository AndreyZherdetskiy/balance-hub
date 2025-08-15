"""Политики доступа (ABAC) как зависимости FastAPI."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.core.constants.error_messages import ErrorMessages
from app.core.deps.auth import get_current_user
from app.models import User


def require_self_or_admin_user(
    user_id: int, current_user: User = Depends(get_current_user)
) -> None:
    """Проверяет доступ: текущий пользователь — владелец ресурса или администратор.

    Args:
        user_id (int): Идентификатор владельца ресурса.
        current_user (User): Текущий пользователь из контекста авторизации.

    Raises:
        HTTPException: 403 если доступ запрещён.
    """
    if current_user.is_admin:
        return
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.ACCESS_DENIED
        )
