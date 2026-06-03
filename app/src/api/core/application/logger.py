from collections.abc import Mapping
import logging
from pathlib import Path
import sys
from typing import Any

from loguru import logger


class InterceptHandler(logging.Handler):
    """Forward stdlib logging -> loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = record.levelno

        # сохраняем оригинальный источник записи stdlib
        extra = {
            "orig_name": record.name,
            "orig_path": record.pathname,
            "orig_func": record.funcName,
            "orig_line": record.lineno,
        }

        logger.bind(**extra).opt(
            depth=2,
            exception=record.exc_info,
        ).log(level, record.getMessage())


def _formatter(record: Mapping[str, Any]) -> str:

    name = record["extra"].get("orig_name", record["name"])
    func = record["extra"].get("orig_func", record["function"])
    line = record["extra"].get("orig_line", record["line"])

    if record["extra"].get("http"):
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level:<7}</level> | "
            "{extra[endpoint]} <level>{extra[method]} {extra[path]} -> {extra[status]} "
            "({extra[duration_ms]}ms, {extra[client]})</level>\n"
        )
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level:<7}</level> | "
        f"{name}:{func}:{line} - "
        "<level>{message}</level>\n"
    )


def setup_logger(
    file_path: str | Path = None,
    level: str | int = "INFO",
    rotation: str = "1 week",
    compression: str = "zip",
) -> None:
    logger.remove()

    if file_path:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            file_path,
            format=_formatter,
            level=level,
            rotation=rotation,
            compression=compression,
            enqueue=True,
            diagnose=False,
            backtrace=False,
            colorize=False,
        )

    # console (with color)
    logger.add(
        sys.stdout,
        format=_formatter,
        level=level,
        enqueue=True,
        diagnose=False,
        backtrace=False,
        colorize=True,
    )

    # interception of stdlib logs and demolition of default handlers
    handler = InterceptHandler()
    logging.captureWarnings(True)
    logging.basicConfig(handlers=[handler], level=0, force=True)

    # spot reconfiguration of popular loggers
    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "httpx",
        "asyncio",
    ):
        lg = logging.getLogger(name)
        lg.handlers = [handler]
        lg.propagate = False
