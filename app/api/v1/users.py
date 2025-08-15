"""Маршруты работы с пользователями."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    ApiDescription,
    ApiErrorResponses,
    ApiSuccessResponses,
    ApiSummary,
    PaginationParamDescriptions,
    PaginationParams,
    UsersPaths,
)
from app.core.deps import get_current_admin, get_current_user, get_user_service
from app.db.session import get_db_session
from app.models import User
from app.schemas import UserCreate, UserPublic, UserUpdate
from app.services import UserService
from app.validators import AccountValidator, UserValidator


router = APIRouter(prefix=UsersPaths.PREFIX, tags=[UsersPaths.TAG])


@router.get(
    UsersPaths.ME,
    response_model=UserPublic,
    summary=ApiSummary.USERS_ME,
    description=ApiDescription.USERS_ME,
    status_code=status.HTTP_200_OK,
    responses={
        200: ApiSuccessResponses.USERS_ME_200,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
    },
)
async def read_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    """Возвращает данные текущего пользователя.

    Args:
        current_user (User): Пользователь из контекста авторизации.

    Returns:
        UserPublic: Профиль пользователя.

    Raises:
        HTTPException: 401 если неавторизован.
    """
    return UserPublic.model_validate(current_user)


@router.post(
    UsersPaths.ADMIN_USERS,
    response_model=UserPublic,
    dependencies=[Depends(get_current_admin)],
    summary=ApiSummary.ADMIN_USERS_CREATE,
    description=ApiDescription.ADMIN_USERS_CREATE,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: ApiSuccessResponses.USERS_CREATE_201,
        400: ApiErrorResponses.INVALID_PARAMS,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
        403: ApiErrorResponses.FORBIDDEN,
    },
)
async def admin_create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    """Создаёт нового пользователя.

    Args:
        payload (UserCreate): Данные пользователя.
        db (AsyncSession): Сессия БД.
        user_service (UserService): Сервис для работы с пользователями.

    Returns:
        UserPublic: Созданный пользователь.

    Raises:
        HTTPException: 400 при некорректных параметрах запроса.
        HTTPException: 401 если неавторизован.
        HTTPException: 403 если недостаточно прав (не админ).
    """
    UserValidator.validate_user_create(payload)

    user = await user_service.create_user(db, payload)
    return UserPublic.model_validate(user)


@router.get(
    UsersPaths.ADMIN_USERS,
    response_model=list[UserPublic],
    dependencies=[Depends(get_current_admin)],
    summary=ApiSummary.ADMIN_USERS_LIST,
    description=ApiDescription.ADMIN_USERS_LIST,
    status_code=status.HTTP_200_OK,
    responses={
        200: ApiSuccessResponses.USERS_LIST_200,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
        403: ApiErrorResponses.FORBIDDEN,
        400: ApiErrorResponses.INVALID_PARAMS,
    },
)
async def admin_list_users(
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
    limit: int = Query(
        PaginationParams.DEFAULT_LIMIT,
        ge=PaginationParams.MIN_LIMIT,
        le=PaginationParams.MAX_LIMIT,
        description=PaginationParamDescriptions.LIMIT,
        examples={
            'default': {
                'summary': 'Значение по умолчанию',
                'value': PaginationParams.DEFAULT_LIMIT,
            }
        },
    ),
    offset: int = Query(
        PaginationParams.DEFAULT_OFFSET,
        ge=PaginationParams.OFFSET,
        description=PaginationParamDescriptions.OFFSET,
        examples={
            'default': {
                'summary': 'Значение по умолчанию',
                'value': PaginationParams.DEFAULT_OFFSET,
            }
        },
    ),
) -> list[UserPublic]:
    """Возвращает список всех пользователей.

    Args:
        db (AsyncSession): Сессия БД.
        user_service (UserService): Сервис для работы с пользователями.
        limit (int): Максимум записей.
        offset (int): Смещение.

    Returns:
        list[UserPublic]: Список пользователей.

    Raises:
        HTTPException: 400 при некорректных параметрах пагинации.
        HTTPException: 401 если неавторизован.
        HTTPException: 403 если недостаточно прав (не админ).
    """
    AccountValidator.validate_pagination_params(limit, offset)

    users = await user_service.get_all_users(db, limit, offset)
    return [UserPublic.model_validate(u) for u in users]


@router.get(
    UsersPaths.ADMIN_USER_ID,
    response_model=UserPublic,
    dependencies=[Depends(get_current_admin)],
    summary=ApiSummary.ADMIN_USERS_GET,
    description=ApiDescription.ADMIN_USERS_GET,
    status_code=status.HTTP_200_OK,
    responses={
        200: ApiSuccessResponses.USER_GET_200,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
        403: ApiErrorResponses.FORBIDDEN,
        404: ApiErrorResponses.USER_NOT_FOUND,
        400: ApiErrorResponses.INVALID_PARAMS,
    },
)
async def admin_get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    """Возвращает пользователя по идентификатору.

    Args:
        user_id (int): Идентификатор пользователя.
        db (AsyncSession): Сессия БД.
        user_service (UserService): Сервис для работы с пользователями.

    Returns:
        UserPublic: Пользователь.

    Raises:
        HTTPException: 400 при некорректных параметрах запроса.
        HTTPException: 401 если неавторизован.
        HTTPException: 403 если недостаточно прав (не админ).
        HTTPException: 404 если пользователь не найден.
    """
    AccountValidator.validate_user_id(user_id)

    user = await user_service.get_user_by_id(db, user_id)
    return UserPublic.model_validate(user)


@router.patch(
    UsersPaths.ADMIN_USER_ID,
    response_model=UserPublic,
    dependencies=[Depends(get_current_admin)],
    summary=ApiSummary.ADMIN_USERS_UPDATE,
    description=ApiDescription.ADMIN_USERS_UPDATE,
    status_code=status.HTTP_200_OK,
    responses={
        200: ApiSuccessResponses.USER_UPDATE_200,
        400: ApiErrorResponses.INVALID_PARAMS,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
        403: ApiErrorResponses.FORBIDDEN,
        404: ApiErrorResponses.USER_NOT_FOUND,
    },
)
async def admin_update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    """Обновляет данные существующего пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        payload (UserUpdate): Поля для обновления.
        db (AsyncSession): Сессия БД.
        user_service (UserService): Сервис для работы с пользователями.

    Returns:
        UserPublic: Обновлённый пользователь.

    Raises:
        HTTPException: 400 при некорректных параметрах запроса.
        HTTPException: 401 если неавторизован.
        HTTPException: 403 если недостаточно прав (не админ).
        HTTPException: 404 если пользователь не найден.
    """
    AccountValidator.validate_user_id(user_id)
    UserValidator.validate_user_update(payload)

    user = await user_service.update_user(db, user_id, payload)
    return UserPublic.model_validate(user)


@router.delete(
    UsersPaths.ADMIN_USER_ID,
    dependencies=[Depends(get_current_admin)],
    summary=ApiSummary.ADMIN_USERS_DELETE,
    description=ApiDescription.ADMIN_USERS_DELETE,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: ApiSuccessResponses.DELETED_204,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
        403: ApiErrorResponses.FORBIDDEN,
        404: ApiErrorResponses.USER_NOT_FOUND,
        400: ApiErrorResponses.INVALID_PARAMS,
    },
)
async def admin_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
) -> Response:
    """Удаляет пользователя по идентификатору.

    Args:
        user_id (int): Идентификатор пользователя.
        db (AsyncSession): Сессия БД.
        user_service (UserService): Сервис для работы с пользователями.

    Returns:
        Response: Статус выполнения операции.

    Raises:
        HTTPException: 400 при некорректных параметрах запроса.
        HTTPException: 401 если неавторизован.
        HTTPException: 403 если недостаточно прав (не админ).
        HTTPException: 404 если пользователь не найден.
    """
    AccountValidator.validate_user_id(user_id)

    await user_service.delete_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
