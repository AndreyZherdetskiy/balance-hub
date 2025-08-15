"""Точка входа FastAPI приложения.

Содержит фабрику приложения и подключение маршрутов, CORS.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import create_api_router
from app.core.config import get_settings
from app.core.errors import DomainError, to_http_exc


def create_app() -> FastAPI:
    """Создаёт и настраивает экземпляр FastAPI.

    Returns:
        FastAPI: Инициализированное приложение с подключёнными middleware и роутерами.
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        description=(
            'Асинхронный REST API для управления пользователями, счетами и платежами.\n\n'
            'Доступные разделы:\n'
            '- Аутентификация\n'
            '- Пользователи (админ)\n'
            '- Счета\n'
            '- Платежи\n'
            '- Вебхук пополнения\n'
        ),
        openapi_tags=[
            {'name': 'auth', 'description': 'Аутентификация и получение JWT токена.'},
            {
                'name': 'users',
                'description': 'Профиль текущего пользователя и админ-операции с пользователями.',
            },
            {
                'name': 'accounts',
                'description': 'Операции со счетами пользователя и админ-доступ к счетам.',
            },
            {
                'name': 'payments',
                'description': 'Просмотр платежей текущего пользователя.',
            },
            {
                'name': 'webhook',
                'description': 'Обработка входящих уведомлений о пополнении от внешней системы.',
            },
        ],
    )

    if settings.cors_origins == ['*']:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

    app.include_router(create_api_router())

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError):
        """Возвращает JSON-ответ для доменных исключений.

        Преобразует `DomainError` в HTTP-ответ через `to_http_exc`.

        Args:
            _ (Request): Входящий запрос (не используется).
            exc (DomainError): Доменное исключение.

        Returns:
            JSONResponse: Ответ с кодом статуса и сообщением об ошибке.
        """
        http_exc = to_http_exc(exc)
        return JSONResponse(status_code=http_exc.status_code, content={'detail': http_exc.detail})

    return app


app = create_app()
