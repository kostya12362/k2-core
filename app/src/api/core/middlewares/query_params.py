from collections.abc import Callable
from urllib.parse import urlencode

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import QueryParams


class QueryStringFlatteningMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request.scope["query_string"] = self.params_to_base(request.query_params)
        response = await call_next(request)
        new_query_params: dict = self.params_from_base(request.query_params)
        request.url.replace_query_params(**new_query_params)
        return response

    @staticmethod
    def params_to_base(query_params: QueryParams) -> bytes:
        flattened = []
        for key, value in query_params.multi_items():
            flattened.extend((key, entry) for entry in value.split(","))
        return urlencode(flattened, doseq=True).encode("utf-8")

    @staticmethod
    def params_from_base(query_params: QueryParams) -> dict:
        query_dict = {}
        for key, value in query_params.multi_items():
            if query_dict.get(key):
                query_dict[key] += f",{value}"
            else:
                query_dict[key] = value
        for key, value in query_dict.items():
            if "," in value:
                query_dict[key] = f"[{value}]"
        return query_dict
