import abc
from typing import Generic, TypeVar

from api.core.schemas import PublicSchema

TDetail = TypeVar("TDetail", bound=PublicSchema)


class BaseMessage(abc.ABC, Generic[TDetail]):
    def __init__(
        self,
        message: str,
        status_code: int,
        code: str,
        detail: TDetail | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        if not code.isupper():
            raise ValueError("Code must be uppercase")
        self.code = code
        self.detail = detail
        self.headers = headers


class ApiHTTPException(BaseMessage, Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
        code: str,
        detail: TDetail | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status_code,
            code=code,
            detail=detail,
            headers=headers,
        )
