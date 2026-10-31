import os
import uuid
import pytest
from sqlalchemy import create_engine, text


@pytest.fixture(autouse=True)
def isolate_external_credentials(request, monkeypatch):
    """Normal tests must never inherit a user's paid API credentials or real app mode."""
    if request.node.get_closest_marker("external"):
        return
    monkeypatch.setenv("APP_MODE", "fixture")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("SEARCH_API_KEY", "")
    monkeypatch.setenv("STUDYFORGE_TRACING", "false")
    monkeypatch.setenv("STUDYFORGE_TRACE_CONTENT", "false")
    monkeypatch.setenv("LANGSMITH_API_KEY", "")
    from app.settings import get_settings

    get_settings.cache_clear()


@pytest.fixture
def database_schema():
    """Each test owns a random schema; never delete the personal library."""
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for isolated PostgreSQL tests")
    engine = create_engine(url, echo=False, hide_parameters=True)
    schema = "sf_test_" + uuid.uuid4().hex
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    try:
        yield engine, schema
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()


@pytest.fixture
def library_url(database_schema):
    from app.db.models import Base

    engine, schema = database_schema
    with engine.begin() as connection:
        connection.execute(text(f'SET LOCAL search_path TO "{schema}", public'))
        # checkfirst would find public tables through search_path and skip creation.
        # Always create each table in the fresh test schema, even after real migrations.
        Base.metadata.create_all(connection, checkfirst=False)
        assert connection.scalar(text("SELECT current_schema()")) == schema
        assert connection.scalar(
            text("SELECT count(*) FROM pg_tables WHERE schemaname=:schema"),
            {"schema": schema},
        ) == len(Base.metadata.tables)
    return engine.url.update_query_dict(
        {"options": f"-csearch_path={schema},public"}
    ).render_as_string(hide_password=False)
