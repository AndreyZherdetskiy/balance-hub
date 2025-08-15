"""Константы, связанные с пагинацией и описания параметров для тестов."""

from __future__ import annotations

from app.core.constants import PaginationParamDescriptions, PaginationParams


class TestPaginationParams(PaginationParams):
    """Константы пагинации для тестов."""

    # Дополнительные константы пагинации для тестов
    INVALID_LIMIT_NEGATIVE = -1
    INVALID_LIMIT_TOO_LARGE = 1000
    INVALID_OFFSET_NEGATIVE = -1

    # Валидные значения для тестов (используйте вместо литералов)
    VALID_LIMIT_MIN = 1
    VALID_LIMIT_10 = 10
    VALID_LIMIT_100 = 100
    VALID_OFFSET_0 = 0
    VALID_OFFSET_50 = 50


class TestPaginationParamDescriptions(PaginationParamDescriptions):
    """Описание параметров пагинации для OpenAPI в тестах."""
