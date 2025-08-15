#!/usr/bin/env python3
"""Универсальный скрипт для автоматического создания init миграции.

Создает корректную init миграцию с правильными импортами и типами данных.
Работает как локально, так и в Docker окружении.
Использует autogenerate Alembic для автоматического определения схемы.
"""

import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_init_migration():
    """Создает init миграцию с правильными настройками."""
    # Определяем окружение
    is_docker = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV") == "true"
    env_prefix = "🐳" if is_docker else "🔧"

    print(
        f"{env_prefix} Создаю init миграцию в {'Docker' if is_docker else 'локальном'} окружении..."
    )

    # Путь к alembic.ini
    alembic_cfg = Config(project_root / "alembic.ini")

    try:
        # Создаем autogenerate миграцию
        command.revision(alembic_cfg, message="init_schema", autogenerate=True)
        print("✅ Init миграция создана успешно!")

        # Теперь исправляем импорты в созданной миграции
        fix_migration_imports(is_docker)

    except Exception as e:
        print(f"❌ Ошибка при создании миграции: {e}")
        sys.exit(1)


def fix_migration_imports(is_docker):
    """Исправляет импорты в созданной миграции."""
    print("🔧 Исправляю импорты в миграции...")

    versions_dir = project_root / "alembic" / "versions"
    if not versions_dir.exists():
        print("❌ Директория versions не найдена")
        return

    # Находим самую новую миграцию
    migration_files = list(versions_dir.glob("*.py"))
    if not migration_files:
        print("❌ Файлы миграций не найдены")
        return

    # Берем самую новую миграцию (по времени создания)
    latest_migration = max(migration_files, key=lambda x: x.stat().st_mtime)
    print(f"📝 Обрабатываю файл: {latest_migration.name}")

    # Читаем содержимое файла
    content = latest_migration.read_text(encoding="utf-8")

    # Заменяем импорты
    if "from alembic import op" in content:
        # Добавляем импорт SafeMoney
        if "from app.db.types import SafeMoney" not in content:
            content = content.replace(
                "from alembic import op\nimport sqlalchemy as sa",
                "from alembic import op\nimport sqlalchemy as sa\nfrom app.db.types import SafeMoney",
            )

        # Заменяем все использования app.db.types.SafeMoney на SafeMoney
        content = content.replace("app.db.types.SafeMoney()", "SafeMoney()")

        # Записываем исправленный файл
        latest_migration.write_text(content, encoding="utf-8")
        print("✅ Импорты исправлены успешно!")

        # В Docker устанавливаем правильные права доступа
        if is_docker:
            os.chmod(latest_migration, 0o666)
            print("✅ Права доступа установлены!")
    else:
        print("⚠️  Структура файла миграции неожиданная, пропускаю исправление")


if __name__ == "__main__":
    create_init_migration()
