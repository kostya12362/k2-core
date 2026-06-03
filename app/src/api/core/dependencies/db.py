from collections.abc import AsyncGenerator, Callable
import dataclasses
import inspect
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import SessionFactory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def _get_dataclass_repository[T](repo_type: type[T]) -> Callable[..., Any]:
    fields = dataclasses.fields(repo_type)

    async def _get_repo(**kwargs: Any) -> T:
        return repo_type(**kwargs)

    _get_repo.__signature__ = inspect.Signature(
        parameters=[
            inspect.Parameter(
                name=f.name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=Depends(get_repository(f.type)),
                annotation=f.type,
            )
            for f in fields
        ],
        return_annotation=repo_type,
    )

    return _get_repo


def get_repository[T](repo_type: type[T]) -> Callable[..., Any]:
    if dataclasses.is_dataclass(repo_type):
        return _get_dataclass_repository(repo_type)

    async def _get_repo(session: AsyncSession = Depends(get_db_session)) -> T:
        return repo_type(session)  # type: ignore[arg-type]

    return _get_repo
