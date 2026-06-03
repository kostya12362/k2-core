from typing import Generic

from pydantic import Field, computed_field

from api.core.schemas.base import PublicSchema, _PublicSchema


class PageMeta(PublicSchema):
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Limit per request")
    offset: int = Field(description="Offset from start")

    @computed_field
    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total

    @computed_field
    @property
    def next_offset(self) -> int | None:
        if not self.has_next:
            return None

        return self.offset + self.limit


class ResponsePage(PublicSchema, Generic[_PublicSchema]):
    data: list[_PublicSchema]
    page: PageMeta


class PaginationParams(PublicSchema):
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
