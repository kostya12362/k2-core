"""
This module is used for representing FastAPI error handlers
that are dispatched automatically by fastapi engine.
"""

from collections.abc import Callable, Coroutine
import traceback
from typing import Any

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from loguru import logger

from api.core.errors.exceptions import ApiHTTPException, NotFound, UnhandledError
from api.core.schemas import ErrorResponse, ErrorResponseMulti


async def custom_base_errors_handler(_: Request, error: ApiHTTPException) -> JSONResponse:
    """This function is called if the BaseError was raised."""
    response = ErrorResponseMulti(
        errors=[ErrorResponse(message=error.message.capitalize(), code=error.code)]
    )
    return JSONResponse(
        response.model_dump(by_alias=True),
        status_code=error.status_code,
        headers=error.headers,
    )


async def python_base_error_handler(_: Request, __: Exception) -> JSONResponse:
    """This function is called if the Exception was raised."""
    logger.error(traceback.format_exc())
    _error = UnhandledError()
    response = ErrorResponseMulti(
        errors=[
            ErrorResponse(
                message=_error.message,
                code=_error.code,
            )
        ]
    )

    return JSONResponse(
        content=jsonable_encoder(response.model_dump(by_alias=True)),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def parser_error(
    error: RequestValidationError | ResponseValidationError,
) -> ErrorResponseMulti:
    return ErrorResponseMulti(
        errors=[
            ErrorResponse(
                message=err["msg"],
                code=err["type"].upper(),
                path=list(err["loc"]),
            )
            for err in error.errors()
        ]
    )


async def request_validation_errors_handler(
    _: Request, error: RequestValidationError
) -> JSONResponse:
    """This function is called if the Pydantic
    validation request error was raised."""
    return JSONResponse(
        content=jsonable_encoder(parser_error(error).model_dump(by_alias=True)),
        status_code=422,
    )


async def response_validation_errors_handler(
    _: Request, error: ResponseValidationError
) -> JSONResponse:
    """This function is called if the
    Pydantic validation response error was raised."""
    logger.error(traceback.format_exc())
    return JSONResponse(
        content=jsonable_encoder(parser_error(error).model_dump(by_alias=True)),
        status_code=422,
    )


async def not_found_errors_handler(request: Request, _: HTTPException) -> JSONResponse:
    return await custom_base_errors_handler(request, NotFound())


MAP_ERROR_HANDLERS: dict[
    int | type[Exception],
    Callable[[Request, Any], Coroutine[Any, Any, Response]],
] = {
    404: not_found_errors_handler,
}

__all__ = (
    "custom_base_errors_handler",
    "python_base_error_handler",
    "request_validation_errors_handler",
    "response_validation_errors_handler",
    "MAP_ERROR_HANDLERS",
)
