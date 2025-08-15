"""DI провайдеры для сервисов приложения."""

from __future__ import annotations

from fastapi import Depends

from app.core.deps.crud import get_account_crud, get_payment_crud, get_user_crud
from app.core.deps.validators import get_user_async_validator
from app.crud.accounts import CRUDAccount
from app.crud.payments import CRUDPayment
from app.crud.users import CRUDUser
from app.services.accounts import AccountService
from app.services.auth import AuthService
from app.services.payments import PaymentService
from app.services.users import UserService
from app.services.webhook import WebhookService
from app.validators.async_ import UserAsyncValidator


def get_user_service(
    users_crud: CRUDUser = Depends(get_user_crud),
    user_validator: UserAsyncValidator = Depends(get_user_async_validator),
) -> UserService:
    """Возвращает инстанс `UserService` с внедрёнными зависимостями.

    Args:
        users_crud (CRUDUser): CRUD-уровень для пользователей.
        user_validator (UserAsyncValidator): Асинхронный валидатор пользователей.

    Returns:
        UserService: Сервис пользователей.
    """
    return UserService(users_crud, user_validator)


def get_account_service(
    accounts_crud: CRUDAccount = Depends(get_account_crud),
    users_crud: CRUDUser = Depends(get_user_crud),
) -> AccountService:
    """Возвращает инстанс `AccountService` с внедрёнными зависимостями.

    Args:
        accounts_crud (CRUDAccount): CRUD-уровень для счетов.
        users_crud (CRUDUser): CRUD-уровень для пользователей.

    Returns:
        AccountService: Сервис счетов.
    """
    return AccountService(accounts_crud, users_crud)


def get_payment_service(
    payments_crud: CRUDPayment = Depends(get_payment_crud),
) -> PaymentService:
    """Возвращает инстанс `PaymentService` с внедрёнными зависимостями.

    Args:
        payments_crud (CRUDPayment): CRUD-уровень для платежей.

    Returns:
        PaymentService: Сервис платежей.
    """
    return PaymentService(payments_crud)


def get_auth_service(users_crud: CRUDUser = Depends(get_user_crud)) -> AuthService:
    """Возвращает инстанс `AuthService` с внедрёнными зависимостями.

    Args:
        users_crud (CRUDUser): CRUD-уровень для пользователей.

    Returns:
        AuthService: Сервис аутентификации.
    """
    return AuthService(users_crud)


def get_webhook_service(
    accounts_crud: CRUDAccount = Depends(get_account_crud),
    payments_crud: CRUDPayment = Depends(get_payment_crud),
    user_validator: UserAsyncValidator = Depends(get_user_async_validator),
) -> WebhookService:
    """Возвращает инстанс `WebhookService` с внедрёнными зависимостями.

    Args:
        accounts_crud (CRUDAccount): CRUD-уровень для счетов.
        payments_crud (CRUDPayment): CRUD-уровень для платежей.
        user_validator (UserAsyncValidator): Валидатор пользователей.

    Returns:
        WebhookService: Сервис вебхуков.
    """
    return WebhookService(accounts_crud, payments_crud, user_validator)
