from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.settings import Settings


def make_database(settings: Settings):
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        hide_parameters=True,
        pool_size=5,
        max_overflow=0,
        pool_pre_ping=True,
    )
    return engine, async_sessionmaker(engine, expire_on_commit=False)
