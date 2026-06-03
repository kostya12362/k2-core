from contextvars import ContextVar
from functools import lru_cache
import importlib
import os
from typing import Any

from fastapi import Request, Response
from pydantic import BaseModel
from starlette.requests import QueryParams

DEFAULT_SETTINGS_MODULE = os.getenv("DEFAULT_SETTINGS_MODULE", "src.config.settings")

request_context: ContextVar[Request] = ContextVar("request_context")
response_context: ContextVar[Response] = ContextVar("response_context")


def get_request() -> Request:
    try:
        return request_context.get()
    except LookupError as err:
        raise RuntimeError("Response context variable is not set") from err


def get_response() -> Response:
    try:
        return response_context.get()
    except LookupError as err:
        raise RuntimeError("Response context variable is not set") from err


@lru_cache
def load_settings() -> BaseModel:
    """
    Load settings based on the `SETTINGS_MODULE` environment variable.
    """
    settings_path = os.getenv("SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)
    module_path, class_name = settings_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def params_from_base(query_params: QueryParams) -> dict:
    query_dict: dict[str, Any] = {}
    for key, value in query_params.multi_items():
        if query_dict.get(key):
            query_dict[key] += f",{value}"
        else:
            query_dict[key] = value
    for key, value in query_dict.items():
        if "," in value:
            query_dict[key] = f"[{value}]"
    return query_dict


settings = load_settings()
