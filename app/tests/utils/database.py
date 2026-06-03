from config import settings
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from models import Base


def create_test_engine() -> AsyncEngine:
    return create_async_engine(
        settings.database.uri,
        echo=False,
        poolclass=NullPool,
    )


async def create_test_database_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def drop_test_database_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)