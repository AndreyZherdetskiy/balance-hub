"""Зависимости аутентификации/авторизации."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.constants.auth import AuthConstants
from app.core.constants.api_paths import AuthPaths
from app.core.constants.error_messages import ErrorMessages
from app.db.session import get_db_session
from app.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AuthPaths.TOKEN_URL)


async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> User:
    """Извлекает текущего пользователя из JWT-токена.

    Декодирует токен, валидирует subject и загружает пользователя из БД. При
    некорректных учётных данных возвращает 401 с заголовком `WWW-Authenticate`.

    Args:
        db (AsyncSession): Асинхронная сессия БД.
        token (str): JWT-токен из схемы OAuth2.

    Returns:
        User: Аутентифицированный пользователь.

    Raises:
        HTTPException: 401 если токен недействителен или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ErrorMessages.NOT_AUTHENTICATED,
        headers={"WWW-Authenticate": AuthConstants.WWW_AUTHENTICATE_SCHEME},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        subject: str | None = payload.get("sub")
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Проверяет, что текущий пользователь является администратором.

    Args:
        user (User): Текущий пользователь из контекста авторизации.

    Returns:
        User: Пользователь с правами администратора.

    Raises:
        HTTPException: 403 если пользователь не является администратором.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.FORBIDDEN
        )
    return user
