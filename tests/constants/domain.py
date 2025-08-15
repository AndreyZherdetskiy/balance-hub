"""Доменные числовые ограничения для тестов."""

from __future__ import annotations

from app.core.constants import DomainConstraints


class TestDomainConstraints(DomainConstraints):
    """Фундаментальные ограничения для доменных сущностей в тестах."""

    # Фундаментальные ограничения для тестов
    # (будут добавлены из core.constants.DomainConstraints)

    # Дополнительные числовые ограничения для тестов
    MAX_INT32 = 2**31 - 1
    MAX_INT64 = 2**63 - 1
