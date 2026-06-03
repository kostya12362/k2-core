from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate_scalars(
    session: AsyncSession,
    stmt: Select[Any],
    *,
    limit: int,
    offset: int,
) -> tuple[list[Any], int]:
    count_stmt = select(func.count()).select_from(
        stmt.order_by(None).limit(None).offset(None).subquery()
    )

    total_result = await session.execute(count_stmt)
    total = int(total_result.scalar_one())

    items_result = await session.execute(stmt.limit(limit).offset(offset))

    return list(items_result.scalars().all()), total
