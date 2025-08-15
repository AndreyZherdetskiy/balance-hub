"""Готовые константы ответов API для OpenAPI (errors/success)."""

from __future__ import annotations

from app.schemas import ErrorResponse

from .error_messages import ErrorMessages


class ApiErrorResponses:
    """Константы ошибочных ответов API для OpenAPI."""

    INVALID_PARAMS = {
        'model': ErrorResponse,
        'description': ErrorMessages.INVALID_PARAMS,
        'content': {'application/json': {'example': {'detail': ErrorMessages.INVALID_PARAMS}}},
    }

    NOT_AUTHENTICATED = {
        'model': ErrorResponse,
        'description': ErrorMessages.NOT_AUTHENTICATED,
        'content': {'application/json': {'example': {'detail': ErrorMessages.NOT_AUTHENTICATED}}},
    }

    FORBIDDEN = {
        'model': ErrorResponse,
        'description': ErrorMessages.FORBIDDEN,
        'content': {'application/json': {'example': {'detail': ErrorMessages.FORBIDDEN}}},
    }

    ACCESS_DENIED = {
        'model': ErrorResponse,
        'description': ErrorMessages.ACCESS_DENIED,
        'content': {'application/json': {'example': {'detail': ErrorMessages.ACCESS_DENIED}}},
    }

    USER_NOT_FOUND = {
        'model': ErrorResponse,
        'description': ErrorMessages.USER_NOT_FOUND,
        'content': {'application/json': {'example': {'detail': ErrorMessages.USER_NOT_FOUND}}},
    }

    INVALID_CREDENTIALS = {
        'model': ErrorResponse,
        'description': ErrorMessages.INVALID_CREDENTIALS,
        'content': {
            'application/json': {'example': {'detail': ErrorMessages.INVALID_CREDENTIALS}}
        },
    }

    INVALID_SIGNATURE = {
        'model': ErrorResponse,
        'description': ErrorMessages.INVALID_SIGNATURE,
        'content': {'application/json': {'example': {'detail': ErrorMessages.INVALID_SIGNATURE}}},
    }

    INVALID_PAYMENT_DATA = {
        'model': ErrorResponse,
        'description': ErrorMessages.INVALID_PAYMENT_DATA,
        'content': {
            'application/json': {'example': {'detail': ErrorMessages.INVALID_PAYMENT_DATA}}
        },
    }

    TRANSACTION_ALREADY_PROCESSED = {
        'model': ErrorResponse,
        'description': ErrorMessages.TRANSACTION_ALREADY_PROCESSED,
        'content': {
            'application/json': {
                'example': {'detail': ErrorMessages.TRANSACTION_ALREADY_PROCESSED}
            }
        },
    }

    DB_CONNECTION_ERROR = {
        'model': ErrorResponse,
        'description': ErrorMessages.DB_CONNECTION_ERROR,
        'content': {
            'application/json': {'example': {'detail': ErrorMessages.DB_CONNECTION_ERROR}}
        },
    }


class ApiSuccessResponses:
    """Константы успешных ответов API для OpenAPI."""

    AUTH_LOGIN_200 = {
        'description': 'Успешная аутентификация',
        'content': {
            'application/json': {
                'example': {
                    'access_token': 'eyJhbGciOi...signature',
                    'token_type': 'bearer',
                }
            }
        },
    }

    HEALTH_APP_200 = {
        'description': 'Приложение доступно',
        'content': {
            'application/json': {'example': {'status': 'ok', 'app': 'balance-hub', 'debug': False}}
        },
    }

    HEALTH_DB_200 = {
        'description': 'Подключение к БД доступно',
        'content': {'application/json': {'example': {'status': 'ok'}}},
    }

    ACCOUNTS_LIST_ABAC_200 = {
        'description': 'Список счетов пользователя',
        'content': {
            'application/json': {
                'example': [
                    {
                        'id': 1,
                        'user_id': 1,
                        'balance': '100.00',
                    }
                ]
            }
        },
    }

    ACCOUNT_CREATE_201 = {
        'description': 'Счёт создан',
        'content': {
            'application/json': {
                'example': {
                    'id': 2,
                    'user_id': 1,
                    'balance': '0.00',
                }
            }
        },
    }

    PAYMENTS_LIST_200 = {
        'description': 'Список платежей',
        'content': {
            'application/json': {
                'example': [
                    {
                        'id': 10,
                        'transaction_id': '5eae174f-7cd0-472c-bd36-35660f00132b',
                        'user_id': 1,
                        'account_id': 1,
                        'amount': '100.00',
                    }
                ]
            }
        },
    }

    USERS_CREATE_201 = {
        'description': 'Создано',
        'content': {
            'application/json': {
                'example': {
                    'id': 3,
                    'email': 'john@example.com',
                    'full_name': 'John Doe',
                }
            }
        },
    }

    USERS_ME_200 = {
        'description': 'Текущий пользователь',
        'content': {
            'application/json': {
                'example': {
                    'id': 1,
                    'email': 'user@example.com',
                    'full_name': 'Test User',
                    'is_admin': False,
                }
            }
        },
    }

    USERS_LIST_200 = {
        'description': 'Список пользователей',
        'content': {
            'application/json': {
                'example': [
                    {
                        'id': 1,
                        'email': 'user1@example.com',
                        'full_name': 'User One',
                        'is_admin': False,
                    },
                    {
                        'id': 2,
                        'email': 'user2@example.com',
                        'full_name': 'User Two',
                        'is_admin': False,
                    },
                ]
            }
        },
    }

    USER_GET_200 = {
        'description': 'Пользователь',
        'content': {
            'application/json': {
                'example': {
                    'id': 1,
                    'email': 'user@example.com',
                    'full_name': 'Test User',
                    'is_admin': False,
                }
            }
        },
    }

    USER_UPDATE_200 = {
        'description': 'Обновлённый пользователь',
        'content': {
            'application/json': {
                'example': {
                    'id': 1,
                    'email': 'newmail@example.com',
                    'full_name': 'New Name',
                    'is_admin': False,
                }
            }
        },
    }

    WEBHOOK_PAYMENT_201 = {
        'description': 'Успешная обработка',
        'content': {
            'application/json': {
                'example': {
                    'id': 10,
                    'transaction_id': '5eae174f-7cd0-472c-bd36-35660f00132b',
                    'user_id': 1,
                    'account_id': 1,
                    'amount': '100.00',
                }
            }
        },
    }

    DELETED_204 = {'description': 'Удалено'}
