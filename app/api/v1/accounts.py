"""Маршруты для работы со счетами пользователей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    AccountsPaths,
    ApiDescription,
    ApiErrorResponses,
    ApiSuccessResponses,
    ApiSummary,
    PaginationParamDescriptions,
    PaginationParams,
)
from app.core.deps import get_account_service, get_current_admin, require_self_or_admin_user
from app.db.session import get_db_session
from app.schemas import AccountPublic
from app.services import AccountService
from app.validators import AccountValidator


router = APIRouter(prefix=AccountsPaths.PREFIX, tags=[AccountsPaths.TAG])


@router.get(
    AccountsPaths.USERS_ACCOUNTS,
    response_model=list[AccountPublic],
    summary=ApiSummary.ACCOUNTS_LIST_ABAC,
    description=ApiDescription.ACCOUNTS_LIST_ABAC,
    status_code=status.HTTP_200_OK,
    responses={
        200: ApiSuccessResponses.ACCOUNTS_LIST_ABAC_200,
        400: ApiErrorResponses.INVALID_PARAMS,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
        403: ApiErrorResponses.ACCESS_DENIED,
        404: ApiErrorResponses.USER_NOT_FOUND,
    },
)
async def list_user_accounts_abac(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    account_service: AccountService = Depends(get_account_service),
    _abac: None = Depends(require_self_or_admin_user),
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
) -> list[AccountPublic]:
    """Получает список счетов пользователя с политикой ABAC (сам владелец или админ).

    Args:
        user_id (int): Идентификатор пользователя.
        db (AsyncSession): Сессия БД.
        account_service (AccountService): Сервис для работы со счетами.
        _abac (None): Зависимость для проверки ABAC.
        limit (int): Максимум записей.
        offset (int): Смещение.

    Returns:
        list[AccountPublic]: Список счетов пользователя.

    Raises:
        HTTPException: 400 при некорректных параметрах пагинации.
        HTTPException: 401 если неавторизован.
        HTTPException: 403 если доступ запрещён (не владелец и не админ).
        HTTPException: 404 если пользователь не найден.
    """
    AccountValidator.validate_user_id(user_id)
    AccountValidator.validate_pagination_params(limit, offset)

    accounts = await account_service.get_user_accounts(db, user_id, limit, offset)
    return [AccountPublic.model_validate(a) for a in accounts]


@router.post(
    AccountsPaths.ADMIN_USERS_ACCOUNTS,
    response_model=AccountPublic,
    dependencies=[Depends(get_current_admin)],
    summary=ApiSummary.ADMIN_CREATE_ACCOUNT,
    description=ApiDescription.ADMIN_CREATE_ACCOUNT,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: ApiSuccessResponses.ACCOUNT_CREATE_201,
        400: ApiErrorResponses.INVALID_PARAMS,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
        403: ApiErrorResponses.FORBIDDEN,
        404: ApiErrorResponses.USER_NOT_FOUND,
    },
)
async def admin_create_account(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    account_service: AccountService = Depends(get_account_service),
) -> AccountPublic:
    """Создает новый счет для пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        db (AsyncSession): Сессия БД.
        account_service (AccountService): Сервис для работы со счетами.

    Returns:
        AccountPublic: Созданный счет.

    Raises:
        HTTPException: 400 при некорректных параметрах запроса.
        HTTPException: 401 если неавторизован.
        HTTPException: 403 если недостаточно прав (не админ).
        HTTPException: 404 если пользователь не найден.
    """
    AccountValidator.validate_user_id(user_id)

    account = await account_service.create_account_for_user(db, user_id)
    return AccountPublic.model_validate(account)
