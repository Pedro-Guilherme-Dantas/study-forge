import importlib
import pytest
from sqlalchemy import text


@pytest.mark.integration
def test_dependency_imports_and_real_vector(database_schema):
    for name in (
        "fastapi",
        "pydantic",
        "sqlalchemy",
        "langgraph",
        "langchain",
        "langchain_google_genai",
        "google.genai",
        "trafilatura",
        "markdown_it",
    ):
        importlib.import_module(name)
    engine, schema = database_schema
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.execute(
            text(f'CREATE TABLE "{schema}".vectors (id int, value vector(3))')
        )
        connection.execute(
            text(
                f"INSERT INTO \"{schema}\".vectors VALUES (1, '[1,0,0]'), (2, '[0,1,0]')"
            )
        )
        result = (
            connection.execute(
                text(
                    f"SELECT id FROM \"{schema}\".vectors ORDER BY value <=> '[1,0,0]'::vector"
                )
            )
            .scalars()
            .all()
        )
        assert result == [1, 2]


@pytest.mark.integration
async def test_async_runtime_role_is_not_superuser():
    from app.db.session import make_database
    from app.settings import Settings

    engine, _ = make_database(Settings())
    try:
        async with engine.connect() as connection:
            role = (
                await connection.execute(
                    text(
                        "SELECT current_user, rolsuper FROM pg_roles WHERE rolname = current_user"
                    )
                )
            ).one()
            assert role[0] == "studyforge_runtime" and role[1] is False
            assert (
                await connection.scalar(
                    text("SELECT extversion FROM pg_extension WHERE extname='vector'")
                )
                == "0.8.7"
            )
    finally:
        await engine.dispose()
