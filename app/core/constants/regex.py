"""Регулярные выражения, используемые в проекте."""

from __future__ import annotations


class RegexPatterns:
    """Стандартизированные паттерны регулярных выражений."""

    EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    FULL_NAME = r"^[a-zA-Zа-яА-Я\s'-]+$"
