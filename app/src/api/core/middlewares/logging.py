from collections.abc import Callable
import logging
import time
import traceback

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.types import ASGIApp

from api.core.utils import settings


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        dispatch: DispatchFunction | None = None,
    ) -> None:
        acc = logging.getLogger("uvicorn.access")
        acc.handlers.clear()
        acc.propagate = False
        acc.disabled = True
        super().__init__(app, dispatch=dispatch)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        except Exception:
            if settings.debug:
                logger.exception(traceback.format_exc())
            raise  # ← всегда пробрасываем, не глотаем
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            route = getattr(request.scope, "path", request.url.path)
            endpoint_fn = getattr(request.scope.get("endpoint"), "__name__", "-")
            endpoint_mod = getattr(request.scope.get("endpoint"), "__module__", "-")
            query_params = request.scope.get("query_string", b"").decode("utf-8")

            logger.bind(
                http=True,
                method=request.method,
                path=f"{route}?{query_params}" if query_params else route,
                endpoint=f"{endpoint_mod}.{endpoint_fn}",
                status=getattr(response, "status_code", 500),
                client=(request.client.host if request.client else "-"),
                duration_ms=duration_ms,
            ).info("")
