from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings

engine = create_async_engine(settings.database.uri, echo=False)

SessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
