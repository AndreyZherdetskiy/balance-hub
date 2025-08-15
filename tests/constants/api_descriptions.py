"""Константы summary/description для эндпойнтов OpenAPI."""

from __future__ import annotations

from app.core.constants import ApiDescription, ApiSummary


class TestApiSummary(ApiSummary):
    """Константы summary для тестов эндпойнтов OpenAPI."""


class TestApiDescription(ApiDescription):
    """Константы description для тестов эндпойнтов OpenAPI."""
