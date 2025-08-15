"""Маршруты для работы с платежами."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    ApiDescription,
    ApiErrorResponses,
    ApiSuccessResponses,
    ApiSummary,
    PaginationParamDescriptions,
    PaginationParams,
    PaymentsPaths,
)
from app.core.deps import get_current_user, get_payment_service
from app.db.session import get_db_session
from app.models import User
from app.schemas import PaymentPublic
from app.services import PaymentService
from app.validators import AccountValidator


router = APIRouter(prefix=PaymentsPaths.PREFIX, tags=[PaymentsPaths.TAG])


@router.get(
    PaymentsPaths.LIST,
    response_model=list[PaymentPublic],
    summary=ApiSummary.PAYMENTS_LIST,
    description=ApiDescription.PAYMENTS_LIST,
    status_code=status.HTTP_200_OK,
    responses={
        200: ApiSuccessResponses.PAYMENTS_LIST_200,
        400: ApiErrorResponses.INVALID_PARAMS,
        401: ApiErrorResponses.NOT_AUTHENTICATED,
    },
)
async def list_my_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    payment_service: PaymentService = Depends(get_payment_service),
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
) -> list[PaymentPublic]:
    """Получает список платежей текущего пользователя.

    Args:
        current_user (User): Пользователь из контекста авторизации.
        db (AsyncSession): Сессия БД.
        payment_service (PaymentService): Сервис для работы с платежами.
        limit (int): Максимум записей.
        offset (int): Смещение.

    Returns:
        list[PaymentPublic]: Список платежей.

    Raises:
        HTTPException: 400 при некорректных параметрах пагинации.
        HTTPException: 401 если неавторизован.
    """
    AccountValidator.validate_pagination_params(limit, offset)

    payments = await payment_service.get_user_payments(db, current_user.id, limit, offset)
    return [PaymentPublic.model_validate(p) for p in payments]
