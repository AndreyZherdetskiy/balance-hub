"""Тесты для обработки ошибок."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.core.errors import (
    AuthError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
    to_http_exc,
)
from tests.constants import TestErrorMessages, TestFieldConstraints, TestValidationData


class TestDomainErrors:
    """Тесты для доменных исключений."""

    def test_domain_error_inheritance(self) -> None:
        """Тест наследования доменных исключений."""
        assert issubclass(NotFoundError, DomainError)
        assert issubclass(ForbiddenError, DomainError)
        assert issubclass(AuthError, DomainError)
        assert issubclass(ValidationError, DomainError)
        assert issubclass(ServiceUnavailableError, DomainError)

    def test_domain_error_creation(self) -> None:
        """Тест создания доменных исключений."""
        not_found = NotFoundError(TestValidationData.USER_NOT_FOUND_EN)
        forbidden = ForbiddenError(TestValidationData.ACCESS_DENIED_EN)
        auth_error = AuthError(TestValidationData.INVALID_CREDENTIALS_EN)
        validation_error = ValidationError(TestValidationData.INVALID_DATA_EN)
        service_error = ServiceUnavailableError(TestValidationData.DB_UNAVAILABLE_EN)

        assert str(not_found) == TestValidationData.USER_NOT_FOUND_EN
        assert str(forbidden) == TestValidationData.ACCESS_DENIED_EN
        assert str(auth_error) == TestValidationData.INVALID_CREDENTIALS_EN
        assert str(validation_error) == TestValidationData.INVALID_DATA_EN
        assert str(service_error) == TestValidationData.DB_UNAVAILABLE_EN

    def test_domain_error_empty_message(self) -> None:
        """Тест доменного исключения с пустым сообщением."""
        not_found = NotFoundError("")
        assert str(not_found) == ""


class TestToHttpExc:
    """Тесты для функции to_http_exc."""

    def test_to_http_exc_not_found(self) -> None:
        """Тест преобразования NotFoundError в HTTPException."""
        error = NotFoundError(TestValidationData.USER_NOT_FOUND_EN)
        http_exc = to_http_exc(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        assert http_exc.detail == TestValidationData.USER_NOT_FOUND_EN

    def test_to_http_exc_not_found_default_message(self) -> None:
        """Тест NotFoundError с пустым сообщением."""
        error = NotFoundError("")
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        assert http_exc.detail == TestErrorMessages.NOT_FOUND

    def test_to_http_exc_forbidden(self) -> None:
        """Тест преобразования ForbiddenError в HTTPException."""
        error = ForbiddenError(TestValidationData.ACCESS_DENIED_EN)
        http_exc = to_http_exc(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_403_FORBIDDEN
        assert http_exc.detail == TestValidationData.ACCESS_DENIED_EN

    def test_to_http_exc_forbidden_default_message(self) -> None:
        """Тест ForbiddenError с пустым сообщением."""
        error = ForbiddenError("")
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_403_FORBIDDEN
        assert http_exc.detail == TestErrorMessages.FORBIDDEN

    def test_to_http_exc_auth_error(self) -> None:
        """Тест преобразования AuthError в HTTPException."""
        error = AuthError(TestValidationData.INVALID_CREDENTIALS_EN)
        http_exc = to_http_exc(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert http_exc.detail == TestValidationData.INVALID_CREDENTIALS_EN

    def test_to_http_exc_auth_error_default_message(self) -> None:
        """Тест AuthError с пустым сообщением."""
        error = AuthError("")
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert http_exc.detail == TestErrorMessages.NOT_AUTHENTICATED

    def test_to_http_exc_validation_error(self) -> None:
        """Тест преобразования ValidationError в HTTPException."""
        error = ValidationError(TestValidationData.INVALID_DATA_EN)
        http_exc = to_http_exc(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail == TestValidationData.INVALID_DATA_EN

    def test_to_http_exc_validation_error_default_message(self) -> None:
        """Тест ValidationError с пустым сообщением."""
        error = ValidationError("")
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail == TestErrorMessages.INVALID_PARAMS

    def test_to_http_exc_service_unavailable_error(self) -> None:
        """Тест преобразования ServiceUnavailableError в HTTPException."""
        error = ServiceUnavailableError(TestValidationData.DB_UNAVAILABLE_EN)
        http_exc = to_http_exc(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert http_exc.detail == TestValidationData.DB_UNAVAILABLE_EN

    def test_to_http_exc_service_unavailable_error_default_message(self) -> None:
        """Тест ServiceUnavailableError с пустым сообщением."""
        error = ServiceUnavailableError("")
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert http_exc.detail == TestErrorMessages.DB_CONNECTION_ERROR

    def test_to_http_exc_fallback_unknown_error(self) -> None:
        """Тест fallback для неизвестных доменных ошибок."""

        class CustomDomainError(DomainError):
            pass

        error = CustomDomainError(TestValidationData.CUSTOM_ERROR_MESSAGE)
        http_exc = to_http_exc(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail == TestValidationData.CUSTOM_ERROR_MESSAGE

    def test_to_http_exc_fallback_empty_message(self) -> None:
        """Тест fallback для неизвестных доменных ошибок с пустым сообщением."""

        class CustomDomainError(DomainError):
            pass

        error = CustomDomainError("")
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail == TestErrorMessages.INVALID_PARAMS

    def test_to_http_exc_with_special_characters(self) -> None:
        """Тест с специальными символами в сообщении."""
        error = ValidationError(TestValidationData.SPECIAL_CHARS_MESSAGE)
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail == TestValidationData.SPECIAL_CHARS_MESSAGE

    def test_to_http_exc_with_unicode(self) -> None:
        """Тест с Unicode символами в сообщении."""
        error = NotFoundError(TestValidationData.NOT_FOUND_RU)
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        assert http_exc.detail == TestValidationData.NOT_FOUND_RU

    def test_to_http_exc_with_long_message(self) -> None:
        """Тест с длинным сообщением."""
        long_message = (
            TestValidationData.LETTER_A * TestFieldConstraints.LONG_MESSAGE_LENGTH
        )
        error = ValidationError(long_message)
        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail == long_message

    def test_to_http_exc_error_chain(self) -> None:
        """Тест с цепочкой ошибок."""
        cause = ValueError(TestValidationData.ROOT_CAUSE_MESSAGE)
        error = ValidationError(TestValidationData.VALIDATION_FAILED_MESSAGE)
        error.__cause__ = cause

        http_exc = to_http_exc(error)

        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail == TestValidationData.VALIDATION_FAILED_MESSAGE
        assert error.__cause__ is cause
