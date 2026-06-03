from collections.abc import Iterable
from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Lifespan

from api.core.errors import (
    MAP_ERROR_HANDLERS,
    ApiHTTPException,
    custom_base_errors_handler,
    python_base_error_handler,
    request_validation_errors_handler,
    response_validation_errors_handler,
)
from api.core.middlewares import (
    LoggingMiddleware,
    QueryStringFlatteningMiddleware,
    RequestResponseContextMiddleware,
    ResponseTimeMiddleware,
)
from api.core.utils import settings

from .logger import setup_logger
from .openapi import custom_openapi

__all__ = ("create",)


def create(
    rest_routers: Iterable[APIRouter],
    lifespan: Lifespan[FastAPI] | None = None,
    middlewares: Iterable[BaseHTTPMiddleware] = None,
    **kwargs: Any,
) -> FastAPI:
    """The application factory using FastAPI framework.
    🎉 Only passing routes is mandatory to start.
    """
    app = FastAPI(
        debug=settings.debug,
        title=settings.public_api.name,
        lifespan=lifespan,
        docs_url=settings.public_api.urls.docs,
        redoc_url=settings.public_api.urls.redoc,
        exception_handlers=MAP_ERROR_HANDLERS,
        **kwargs,
    )
    setup_logger(
        level=settings.logger.level if not settings.debug else "DEBUG",
    )

    # ========= Error Handlers =========
    # Extend FastAPI default error handlers

    app.exception_handler(RequestValidationError)(request_validation_errors_handler)
    app.exception_handler(ResponseValidationError)(response_validation_errors_handler)
    app.exception_handler(ApiHTTPException)(custom_base_errors_handler)
    app.exception_handler(ValidationError)(response_validation_errors_handler)
    if settings.debug is False:
        app.exception_handler(Exception)(python_base_error_handler)

    # Include REST API routers
    for router in rest_routers:
        app.include_router(router)

    # ========= Middleware =========
    # Setup middlewares
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.public_api.cors.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ResponseTimeMiddleware)
    app.add_middleware(RequestResponseContextMiddleware)
    app.add_middleware(QueryStringFlatteningMiddleware)
    for i in middlewares or []:
        app.add_middleware(i)
    custom_openapi(app)

    return app
