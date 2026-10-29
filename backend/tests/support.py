"""Shared integration setup; never import one test module from another for setup."""

from app.db.session import make_database
from app.ingestion.service import IngestionService
from app.operations import Executor
from app.providers.gemini import GeminiProvider
from app.settings import Settings


def service_for(url, provider=None):
    settings = Settings(
        app_mode="fixture",
        gemini_api_key="",
        search_api_key="",
        database_url=url,
        chunk_target=100,
        chunk_max=160,
        chunk_overlap=10,
    )
    engine, database = make_database(settings)
    executor = Executor(1, 6)
    service = IngestionService(
        settings,
        database,
        executor,
        provider or GeminiProvider(settings),
        "test-instance",
    )
    return engine, database, executor, service
