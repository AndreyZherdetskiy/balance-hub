"""DI провайдеры для CRUD-объектов."""

from __future__ import annotations

from app.crud.accounts import CRUDAccount, crud_account
from app.crud.payments import CRUDPayment, crud_payment
from app.crud.users import CRUDUser, crud_user


def get_user_crud() -> CRUDUser:
    return crud_user


def get_account_crud() -> CRUDAccount:
    return crud_account


def get_payment_crud() -> CRUDPayment:
    return crud_payment
