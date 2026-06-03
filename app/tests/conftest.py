from collections.abc import AsyncGenerator

from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from utils.database import (
    create_test_database_schema,
    create_test_engine,
    drop_test_database_schema,
)

from api.app import app
from api.core.dependencies import get_db_session


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_test_engine()

    await create_test_database_schema(engine)

    yield engine

    await drop_test_database_schema(engine)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session_factory(test_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(autouse=True)
async def clean_database(test_engine) -> AsyncGenerator[None]:
    await create_test_database_schema(test_engine)
    yield


@pytest_asyncio.fixture
async def client(db_session_factory):
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with db_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()
