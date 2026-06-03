from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Query

from api.core.schemas.pagination import PaginationParams


def pagination_dependency(
    *,
    default_limit: int = 100,
    max_limit: int = 500,
) -> Callable[..., PaginationParams]:
    def _get_pagination(
        limit: int = Query(default=default_limit, ge=1, le=max_limit),
        offset: int = Query(default=0, ge=0),
    ) -> PaginationParams:
        return PaginationParams(
            limit=limit,
            offset=offset,
        )

    return _get_pagination


get_pagination = pagination_dependency(default_limit=100, max_limit=500)


Pagination = Annotated[PaginationParams, Depends(get_pagination)]
