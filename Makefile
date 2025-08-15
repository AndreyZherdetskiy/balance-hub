# BalanceHub — Make команды для локального и Docker запуска

.PHONY: help \
        local-env local-db-up local-wait-db local-migrate-init local-migrate local-up \
        docker-env docker-build docker-db-up docker-wait-db docker-migrate-init docker-migrate docker-up \
        docker-down

# Можно переопределить DC на командной строке, если используется legacy docker-compose
# Пример: make docker-up DC=docker-compose
DC ?= docker compose
PY = poetry run

# Определяем UID и GID для Docker
UID ?= $(shell id -u)
GID ?= $(shell id -g)

help:
	@echo "\nBalanceHub — команды Make"
	@echo "---------------------------------------"
	@echo "Локальный workflow:"
	@echo "  local-env         — создание .env.local"
	@echo "  local-db-up       — запуск PostgreSQL (Docker)"
	@echo "  local-wait-db     — ожидание готовности БД"
	@echo "  local-migrate-init— создание init миграции"
	@echo "  local-migrate     — применение миграций"
	@echo "  local-up          — запуск API (полный workflow)"
	@echo ""
	@echo "Docker workflow:"
	@echo "  docker-env        — создание .env.docker"
	@echo "  docker-build      — сборка образов"
	@echo "  docker-db-up      — запуск PostgreSQL"
	@echo "  docker-wait-db    — ожидание готовности БД"
	@echo "  docker-migrate-init— создание init миграции"
	@echo "  docker-migrate    — применение миграций"
	@echo "  docker-up         — запуск приложения (полный workflow)"
	@echo "  docker-down       — остановка и очистка сервисов"

# ----------------------------
# Локальный (host) workflow
# ----------------------------

local-env:
	@echo "🔧 Настройка локального окружения..."
	@if [ ! -f .env.local ] && [ -f .env.local.example ]; then \
		echo "Создаю .env.local из .env.local.example"; \
		cp .env.local.example .env.local; \
	fi

local-db-up: local-env
	@echo "🗄️  Запуск PostgreSQL через Docker..."
	$(DC) up -d db

local-db-down:
	@echo "🗄️  Остановка PostgreSQL..."
	$(DC) down db

local-db-down-v:
	@echo "🗄️  Остановка PostgreSQL..."
	$(DC) down -v db

local-wait-db: local-db-up
	@echo "⏳ Ожидаю готовности PostgreSQL..."; \
	until $(DC) exec -T db pg_isready -U postgres >/dev/null 2>&1; do \
		sleep 1; \
	done; \
	echo "✅ PostgreSQL готов"

local-migrate-init: local-wait-db
	@echo "📝 Проверка init миграции..."
	@if [ -z "$(shell ls -A alembic/versions 2>/dev/null)" ]; then \
		echo "Создаю init миграцию..."; \
		$(PY) python scripts/create_init_migration.py; \
	else \
		echo "✅ Init миграция уже существует"; \
	fi

local-migrate: local-migrate-init
	@echo "🔄 Применение миграций..."
	$(PY) alembic upgrade head

local-migrate-down:
	@echo "🔄 Откат миграций..."
	$(PY) alembic downgrade -1

local-up: local-migrate
	@echo "🚀 Запуск локального API..."
	poetry config virtualenvs.in-project true
	poetry config virtualenvs.create true
	poetry env use python3.10
	poetry install --no-interaction --no-ansi
	@echo "Swagger: http://127.0.0.1:8000/docs"
	$(PY) uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

local-seed: local-db-up local-migrate
	$(PY) python -m scripts.seed

local-logs-db:
	$(DC) logs -f db

# ----------------------------
# Docker workflow
# ----------------------------

docker-env:
	@echo "🐳 Настройка Docker окружения..."
	@if [ ! -f .env.docker ] && [ -f .env.docker.example ]; then \
		echo "Создаю .env.docker из .env.docker.example"; \
		cp .env.docker.example .env.docker; \
	fi

docker-build: docker-env
	@echo "🔨 Сборка Docker образов..."
	UID=$(UID) GID=$(GID) $(DC) build

docker-db-up: docker-build
	@echo "🗄️  Запуск PostgreSQL в Docker..."
	$(DC) up -d db

docker-wait-db: docker-db-up
	@echo "⏳ Ожидаю готовности PostgreSQL..."; \
	until $(DC) exec -T db pg_isready -U postgres >/dev/null 2>&1; do \
		sleep 1; \
	done; \
	echo "✅ PostgreSQL готов"

docker-migrate-init: docker-wait-db
	@echo "📝 Проверка init миграции в Docker..."
	@if [ -z "$(shell ls -A alembic/versions 2>/dev/null)" ]; then \
		echo "Создаю init миграцию в контейнере..."; \
		$(DC) run --rm app python scripts/create_init_migration.py; \
	else \
		echo "✅ Init миграция уже существует"; \
	fi

docker-migrate: docker-migrate-init
	@echo "🔄 Применение миграций в Docker..."
	$(DC) run --rm app alembic upgrade head

docker-migrate-down:
	@echo "🔄 Откат миграций в Docker..."
	$(DC) run --rm app alembic downgrade -1

docker-up: docker-migrate
	@echo "🚀 Запуск приложения в Docker..."
	UID=$(UID) GID=$(GID) $(DC) up -d app
	@echo "API:     http://localhost:8000"
	@echo "Swagger: http://localhost:8000/docs"

docker-down:
	@echo "🛑 Остановка Docker сервисов..."
	$(DC) down

docker-down-v:
	@echo "🛑 Остановка Docker сервисов..."
	$(DC) down -v

docker-seed: docker-db-up docker-wait-db docker-migrate
	$(DC) run --rm app python -m scripts.seed

docker-logs-app:
	$(DC) logs -f app

docker-logs-db:
	$(DC) logs -f db
