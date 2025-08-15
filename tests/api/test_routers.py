"""Тесты для роутеров API."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routers import create_api_router
from tests.constants import (
    TestAccountsPaths,
    TestAuthPaths,
    TestHealthPaths,
    TestNumericConstants,
    TestPaymentsPaths,
    TestUsersPaths,
    TestWebhookPaths,
)


class TestApiRouter:
    """Тесты для главного роутера API."""

    def test_create_api_router(self) -> None:
        """Создается корректный экземпляр роутера."""
        router = create_api_router()
        assert isinstance(router, APIRouter)

    def test_api_router_has_routes(self) -> None:
        """Роутер содержит маршруты."""
        router = create_api_router()
        assert len(router.routes) > TestNumericConstants.COUNT_EMPTY

    def test_api_router_no_prefix(self) -> None:
        """Главный роутер не имеет собственного префикса."""
        router = create_api_router()
        assert router.prefix == ""

    def test_api_router_no_tags(self) -> None:
        """Главный роутер не имеет собственных тегов."""
        router = create_api_router()
        assert router.tags == []

    def test_api_router_includes_all_modules(self) -> None:
        """В роутере присутствуют разделы health, auth, users, admin, webhook, payments."""
        router = create_api_router()
        route_paths = [route.path for route in router.routes if hasattr(route, "path")]

        expected_prefixes = [
            f"{TestHealthPaths.PREFIX}{TestHealthPaths.HEALTH}",
            TestAuthPaths.PREFIX,
            TestUsersPaths.USERS_PREFIX,
            TestUsersPaths.ADMIN_PREFIX,
            TestWebhookPaths.PREFIX,
            f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}",
        ]

        for prefix in expected_prefixes:
            assert any(path.startswith(prefix) for path in route_paths), (
                f"No routes found for {prefix}"
            )

    def test_api_router_health_endpoints(self) -> None:
        """Включены health эндпоинты."""
        router = create_api_router()
        route_paths = [route.path for route in router.routes if hasattr(route, "path")]

        assert f"{TestHealthPaths.PREFIX}{TestHealthPaths.HEALTH}" in route_paths
        assert f"{TestHealthPaths.PREFIX}{TestHealthPaths.HEALTH_DB}" in route_paths

    def test_api_router_auth_endpoints(self) -> None:
        """Включены auth эндпоинты."""
        router = create_api_router()
        route_paths = [route.path for route in router.routes if hasattr(route, "path")]

        assert f"{TestAuthPaths.PREFIX}{TestAuthPaths.LOGIN}" in route_paths

    def test_api_router_users_endpoints(self) -> None:
        """Включены users эндпоинты."""
        router = create_api_router()
        route_paths = [route.path for route in router.routes if hasattr(route, "path")]

        assert f"{TestUsersPaths.PREFIX}{TestUsersPaths.ME}" in route_paths
        assert any(
            f"{TestUsersPaths.PREFIX}{TestUsersPaths.ADMIN_USERS}" in path
            for path in route_paths
        )

    def test_api_router_accounts_endpoints(self) -> None:
        """Включены accounts эндпоинты."""
        router = create_api_router()
        route_paths = [route.path for route in router.routes if hasattr(route, "path")]

        assert any(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.USERS_ACCOUNTS}" in path
            for path in route_paths
        )
        assert any(
            f"{TestAccountsPaths.PREFIX}{TestAccountsPaths.ADMIN_USERS_ACCOUNTS}"
            in path
            for path in route_paths
        )

    def test_api_router_payments_endpoints(self) -> None:
        """Включены payments эндпоинты."""
        router = create_api_router()
        route_paths = [route.path for route in router.routes if hasattr(route, "path")]

        assert f"{TestPaymentsPaths.PREFIX}{TestPaymentsPaths.LIST}" in route_paths

    def test_api_router_webhook_endpoints(self) -> None:
        """Включены webhook эндпоинты."""
        router = create_api_router()
        route_paths = [route.path for route in router.routes if hasattr(route, "path")]

        assert f"{TestWebhookPaths.PREFIX}{TestWebhookPaths.PAYMENT}" in route_paths

    def test_api_router_methods(self) -> None:
        """Присутствуют основные HTTP методы."""
        router = create_api_router()

        methods = set()
        for route in router.routes:
            if hasattr(route, "methods"):
                methods.update(route.methods)

        expected_methods = {"GET", "POST", "PATCH", "DELETE"}
        for method in expected_methods:
            assert method in methods, f"Method {method} not found in router"

    def test_api_router_dependencies(self) -> None:
        """На верхнем уровне нет глобальных зависимостей."""
        router = create_api_router()
        assert router.dependencies == []

    def test_api_router_response_models(self) -> None:
        """Часть маршрутов определяет модели ответа."""
        router = create_api_router()

        routes_with_response_models = 0
        for route in router.routes:
            if hasattr(route, "response_model") and route.response_model:
                routes_with_response_models += 1

        assert routes_with_response_models > TestNumericConstants.COUNT_EMPTY

    def test_api_router_openapi_tags(self) -> None:
        """Часть маршрутов определяет OpenAPI теги."""
        router = create_api_router()

        routes_with_tags = 0
        for route in router.routes:
            if hasattr(route, "tags") and route.tags:
                routes_with_tags += 1

        assert routes_with_tags > TestNumericConstants.COUNT_EMPTY

    def test_api_router_operation_ids(self) -> None:
        """Operation ID уникальны среди маршрутов, где они заданы."""
        router = create_api_router()

        operation_ids = set()
        for route in router.routes:
            if hasattr(route, "operation_id") and route.operation_id:
                operation_ids.add(route.operation_id)

        routes_with_operation_id = sum(
            1
            for route in router.routes
            if hasattr(route, "operation_id") and route.operation_id
        )
        assert len(operation_ids) == routes_with_operation_id

    def test_api_router_summary_and_description(self) -> None:
        """Часть маршрутов содержит summary/description для OpenAPI."""
        router = create_api_router()

        routes_with_summary = 0
        routes_with_description = 0

        for route in router.routes:
            if hasattr(route, "summary") and route.summary:
                routes_with_summary += 1
            if hasattr(route, "description") and route.description:
                routes_with_description += 1

        assert (
            routes_with_summary > TestNumericConstants.COUNT_EMPTY
            or routes_with_description > TestNumericConstants.COUNT_EMPTY
        )

    def test_api_router_status_codes(self) -> None:
        """Часть маршрутов определяет статус-коды ответов."""
        router = create_api_router()

        routes_with_status_code = 0
        for route in router.routes:
            if hasattr(route, "status_code") and route.status_code:
                routes_with_status_code += 1

        assert routes_with_status_code > TestNumericConstants.COUNT_EMPTY
