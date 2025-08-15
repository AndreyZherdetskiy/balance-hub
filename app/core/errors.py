"""Доменные исключения и маппинг в HTTP ошибки."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.core.constants.error_messages import ErrorMessages


class DomainError(Exception):
    """Базовое доменное исключение.

    Является родительским для прикладных ошибок домена, которые затем
    транслируются в HTTP-исключения на API-слое.
    """


class NotFoundError(DomainError):
    """Обозначает отсутствие запрошенного объекта."""


class ForbiddenError(DomainError):
    """Обозначает запрет на выполнение операции/доступ."""


class AuthError(DomainError):
    """Обозначает ошибку аутентификации/учётных данных."""


class ValidationError(DomainError):
    """Обозначает ошибку валидации входных данных."""


class ServiceUnavailableError(DomainError):
    """Обозначает временную недоступность сервиса (например, БД)."""


class DuplicateTransactionError(DomainError):
    """Обозначает попытку создать дублирующую транзакцию."""


def to_http_exc(err: DomainError) -> HTTPException:
    """Преобразует доменную ошибку в HTTPException.

    Args:
        err: Исключение доменного слоя.

    Returns:
        HTTPException: Соответствующая HTTP-ошибка.
    """
    if isinstance(err, NotFoundError):
        detail = str(err) if str(err) else ErrorMessages.NOT_FOUND
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if isinstance(err, ForbiddenError):
        detail = str(err) if str(err) else ErrorMessages.FORBIDDEN
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
    if isinstance(err, AuthError):
        detail = str(err) if str(err) else ErrorMessages.NOT_AUTHENTICATED
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
    if isinstance(err, ValidationError):
        detail = str(err) if str(err) else ErrorMessages.INVALID_PARAMS
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    if isinstance(err, ServiceUnavailableError):
        detail = str(err) if str(err) else ErrorMessages.DB_CONNECTION_ERROR
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail
        )
    if isinstance(err, DuplicateTransactionError):
        detail = str(err) if str(err) else ErrorMessages.TRANSACTION_ALREADY_PROCESSED
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    # Fallback: 400 с общим сообщением
    detail = str(err) if str(err) else ErrorMessages.INVALID_PARAMS
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
