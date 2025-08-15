"""Готовые константы ответов API для OpenAPI (errors/success) в тестах."""

from __future__ import annotations

from app.core.constants import ApiErrorResponses, ApiSuccessResponses


class TestApiErrorResponses(ApiErrorResponses):
    """Константы ошибочных ответов API для OpenAPI в тестах."""


class TestApiSuccessResponses(ApiSuccessResponses):
    """Константы успешных ответов API для OpenAPI в тестах."""

    # Статус сообщения
    STATUS_OK = "ok"
