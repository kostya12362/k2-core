from collections.abc import Mapping
from enum import StrEnum
from typing import Annotated, Any, Generic

from pydantic import Field, conlist

from api.core.schemas.base import PublicSchema, _PublicSchema


class ResponseMulti(PublicSchema, Generic[_PublicSchema]):
    """Generic response schema that consist multiple results."""

    data: list[_PublicSchema]


class Response(PublicSchema, Generic[_PublicSchema]):
    """Generic response schema that consist only one result."""

    data: _PublicSchema


class StatusEnum(StrEnum):
    success = "success"
    error = "error"


class TypeResponse(StrEnum):
    message = "message"
    error = "error"
    event = "event"


class MessageResponse(PublicSchema, Generic[_PublicSchema]):
    """Generic response schema that consist only one result."""

    message: str = Field(description="This field represent the message")
    code: str = Field(description="Message code")
    status: StatusEnum | None = Field(
        description="Message status", default=StatusEnum.success
    )
    type: TypeResponse | None = Field(
        description="Type response", default=TypeResponse.message
    )
    detail: _PublicSchema | None = Field(None, description="The message detail")


class ErrorResponse(MessageResponse):
    """Error response schema."""

    status: StatusEnum | None = Field(
        description="Message status", default=StatusEnum.error
    )
    code: str = Field(description="The error code")
    type: TypeResponse | None = Field(
        description="Type response", default=TypeResponse.error
    )
    detail: PublicSchema | None = Field(None, description="The error detail")
    path: list[int | str] = Field(
        description="The path to the field that raised the error",
        default_factory=list,
    )


class EventResponse(MessageResponse):
    """Event response schema."""

    id: str = Field(description="The event id")
    status: StatusEnum | None = Field(
        description="Message status", default=StatusEnum.success
    )
    code: str = Field(description="The event code")
    type: TypeResponse | None = Field(
        description="Type response", default=TypeResponse.event
    )


class ErrorResponseMulti(PublicSchema):
    """The public error response schema that includes multiple objects."""

    errors: Annotated[list[ErrorResponse], conlist(ErrorResponse, min_length=1)]


_Response = Mapping[int | str, dict[str, Any]]

__all__ = (
    "ResponseMulti",
    "Response",
    "MessageResponse",
    "ErrorResponse",
    "EventResponse",
    "ErrorResponseMulti",
    "_Response",
)
