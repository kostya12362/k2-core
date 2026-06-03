from fastapi import status

from api.core.schemas import ApiHTTPException


class NotFound(ApiHTTPException):
    def __init__(
        self,
        message: str | None = "Not found",
        code: str | None = "NOT_FOUND",
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code=code,
        )


class BadRequest(ApiHTTPException):
    def __init__(
        self,
        message: str | None = "Bad request",
        code: str | None = "BAD_REQUEST",
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            code=code,
        )


class Forbidden(ApiHTTPException):
    def __init__(
        self,
        message: str | None = "Forbidden",
        code: str | None = "FORBIDDEN",
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code=code,
        )


class UnhandledError(ApiHTTPException):
    def __init__(
        self,
        message: str | None = "Unhandled error",
        code: str | None = "INTERNAL_SERVER_ERROR",
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=code,
        )
