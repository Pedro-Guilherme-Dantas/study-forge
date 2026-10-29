"""Exercise the frozen Alembic chain without touching the personal library."""

import os
import subprocess
import sys

import pytest
from sqlalchemy import text

from app.db.models import Base


@pytest.mark.integration
def test_fresh_schema_migrates_downgrades_and_matches_model_tables(database_schema):
    engine, schema = database_schema
    with engine.begin() as connection:
        # Otherwise Alembic can discover public.alembic_version via search_path
        # and mistake a completely empty test schema for the migrated library.
        connection.execute(
            text(
                f'CREATE TABLE "{schema}".alembic_version (version_num varchar(32) PRIMARY KEY)'
            )
        )
    env = dict(os.environ)
    env["DATABASE_URL"] = engine.url.update_query_dict(
        {"options": f"-csearch_path={schema},public"}
    ).render_as_string(hide_password=False)

    def migrate(*arguments):
        result = subprocess.run(
            [sys.executable, "-m", "alembic", *arguments],
            env=env,
            capture_output=True,
            timeout=30,
        )
        assert result.returncode == 0, "Isolated migration failed; output withheld"

    def tables():
        with engine.connect() as connection:
            return set(
                connection.scalars(
                    text("SELECT tablename FROM pg_tables WHERE schemaname=:schema"),
                    {"schema": schema},
                )
            )

    migrate("upgrade", "head")
    assert tables() == set(Base.metadata.tables) | {"alembic_version"}
    with engine.connect() as connection:
        assert (
            connection.scalar(
                text(f'SELECT version_num FROM "{schema}".alembic_version')
            )
            == "0002_selection_grants"
        )
    migrate("downgrade", "base")
    assert tables() == {"alembic_version"}
    migrate("upgrade", "head")
    assert tables() == set(Base.metadata.tables) | {"alembic_version"}
