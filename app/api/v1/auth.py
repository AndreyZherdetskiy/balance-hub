"""Маршруты аутентификации."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    ApiDescription,
    ApiErrorResponses,
    ApiSuccessResponses,
    ApiSummary,
    AuthPaths,
)
from app.core.deps import get_auth_service
from app.db.session import get_db_session
from app.schemas import LoginRequest, Token
from app.services.auth import AuthService


router = APIRouter(prefix=AuthPaths.PREFIX, tags=[AuthPaths.TAG])


@router.post(
    AuthPaths.LOGIN,
    response_model=Token,
    summary=ApiSummary.AUTH_LOGIN,
    description=ApiDescription.AUTH_LOGIN,
    status_code=status.HTTP_200_OK,
    responses={
        200: ApiSuccessResponses.AUTH_LOGIN_200,
        400: ApiErrorResponses.INVALID_PARAMS,
        401: ApiErrorResponses.INVALID_CREDENTIALS,
    },
)
async def login_route(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """Аутентифицирует пользователя и возвращает JWT токен.

    Args:
        payload (LoginRequest): Тело запроса с email и паролем.
        db (AsyncSession): Сессия БД.
        auth_service (AuthService): Сервис для аутентификации.

    Returns:
        Token: Объект токена доступа.

    Raises:
        HTTPException: 400 при некорректных параметрах запроса.
        HTTPException: 401 если пара логин/пароль неверна.
    """
    token = await auth_service.authenticate_user(db, payload)
    return Token(access_token=token)
