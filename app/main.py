"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.deps import limiter
from app.api.routers import accounts, auth, payments, users, webhook
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    # CORS
    if settings.cors_origins == ['*']:
        app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
    else:
        app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, lambda request, exc: limiter._rate_limit_exceeded_handler(request, exc))
    app.add_middleware(SlowAPIMiddleware)

    # Routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(accounts.router)
    app.include_router(payments.router)
    app.include_router(webhook.router)

    return app


app = create_app()
