"""Текстовые константы/сообщения об ошибках."""

from __future__ import annotations


class ErrorMessages:
    """Константы сообщений об ошибках."""

    NOT_FOUND = "Объект не найден"
    INVALID_USER_ID = "Некорректный ID пользователя"
    INVALID_PARAMS = "Некорректные параметры"
    INVALID_SIGNATURE = "Неверная подпись"
    INVALID_PAYMENT_DATA = "Некорректные данные платежа"

    # Валидация пагинации
    LIMIT_RANGE_INVALID = "Лимит должен быть числом от 1 до 200"
    OFFSET_MUST_BE_NON_NEGATIVE = "Смещение должно быть неотрицательным числом"

    # Валидация баланса
    BALANCE_MUST_BE_DECIMAL = "Баланс должен быть Decimal"
    BALANCE_CANNOT_BE_NEGATIVE = "Баланс не может быть отрицательным"
    BALANCE_MAX_2_DECIMALS = "Баланс должен иметь максимум 2 знака после запятой"

    # Валидация пользователя
    EMAIL_INVALID = "Некорректный email адрес"
    PASSWORD_MUST_BE_STRING = "Пароль должен быть строкой"
    PASSWORD_WEAK = "Пароль должен содержать минимум 8 символов, букву и цифру"
    FULL_NAME_INVALID = "Некорректное полное имя"

    # Валидация вебхуков/платежей
    AMOUNT_MUST_BE_POSITIVE = "Сумма должна быть положительной"
    INVALID_USER_OR_ACCOUNT_ID = "Некорректные идентификаторы пользователя/счёта"
    INVALID_TRANSACTION_ID = "Некорректный идентификатор транзакции"

    NOT_AUTHENTICATED = "Не авторизован"
    FORBIDDEN = "Недостаточно прав"
    ACCESS_DENIED = "Доступ запрещён"

    USER_NOT_FOUND = "Пользователь не найден"
    TRANSACTION_ALREADY_PROCESSED = "Транзакция уже обработана"
    INVALID_CREDENTIALS = "Неверные учетные данные"
    EMAIL_ALREADY_EXISTS = "Email уже используется"
    DB_CONNECTION_ERROR = "Ошибка подключения к БД"
