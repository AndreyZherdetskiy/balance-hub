"""Константы, связанные с пагинацией и описания параметров."""

from __future__ import annotations


class PaginationParams:
    """Константы пагинации."""

    DEFAULT_LIMIT: int = 50
    MIN_LIMIT: int = 1
    MAX_LIMIT: int = 200
    DEFAULT_OFFSET: int = 0
    OFFSET: int = 0


class PaginationParamDescriptions:
    """Описание параметров пагинации для OpenAPI."""

    LIMIT = 'Максимум записей'
    OFFSET = 'Смещение'
