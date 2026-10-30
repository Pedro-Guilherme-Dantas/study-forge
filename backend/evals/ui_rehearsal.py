"""Opt-in visual rehearsal; disposable schema, authored fixtures, no external calls.

Run with Compose on the already allowed localhost port 5173. This module is never
imported by the product. Scenario words: vazia, parcial, erro; FAIL_ONCE in upload.
"""

import asyncio
import os
import re
from uuid import uuid4

import uvicorn
from sqlalchemy import create_engine, text

from app.db.models import Base
from app.errors import AppError
from app.main import create_app
from app.providers.gemini import GeminiProvider
from app.providers.search import SearchProvider
from app.settings import Settings


class RehearsalProvider(GeminiProvider):
    def __init__(self, settings):
        super().__init__(settings)
        self.failed_upload = False
        self.fail_next = False
        self.delay = 3

    async def embed(self, texts, **kwargs):
        await asyncio.sleep(self.delay)
        upload_failure = any("FAIL_ONCE" in value for value in texts)
        if self.fail_next or (upload_failure and not self.failed_upload):
            self.fail_next = False
            self.failed_upload |= upload_failure
            raise AppError(
                "EXTERNAL_UNAVAILABLE",
                "Falha simulada no serviço de vetores.",
                502,
                "embed",
                True,
            )
        return await super().embed(texts, **kwargs)


class RehearsalSearch(SearchProvider):
    def __init__(self, settings, provider, ingestion_provider):
        super().__init__(settings)
        self.provider = provider
        self.ingestion_provider = ingestion_provider

    async def discover(self, topic, budget):
        await asyncio.sleep(2)
        if "vazia" in topic.casefold():
            return []
        if "erro" in topic.casefold().split():
            raise AppError(
                "SEARCH_UNAVAILABLE",
                "Falha simulada na pesquisa. Tente novamente.",
                502,
                "search",
                True,
            )
        self.provider.fail_next = "parcial" in topic.casefold()
        self.ingestion_provider.fail_next = "ingestão com falha" in topic.casefold()
        candidates = await super().discover(topic, budget)
        if "interromper" in topic.casefold():
            self.ingestion_provider.delay = 20
            return [
                {
                    "title": "[Fixture] Interrupção de ingestão",
                    "url": candidates[0]["url"] + "/interrompido",
                }
            ]
        return candidates


def main():
    if os.environ.get("UI_REHEARSAL") != "1":
        raise SystemExit("UI_REHEARSAL=1 is required")
    admin = create_engine(os.environ["TEST_DATABASE_URL"], hide_parameters=True)
    schema = os.environ.get("UI_SCHEMA", "sf_ui_" + uuid4().hex)
    if not re.fullmatch(r"sf_ui_[a-f0-9]{32}", schema):
        raise SystemExit("Invalid isolated rehearsal schema")
    with admin.begin() as connection:
        exists = connection.scalar(
            text("SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname=:schema)"),
            {"schema": schema},
        )
        if not exists:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{schema}", public'))
        if not exists:
            Base.metadata.create_all(connection, checkfirst=False)
    settings = Settings(
        app_mode="fixture",
        gemini_api_key="",
        search_api_key="",
        database_url=admin.url.update_query_dict(
            {"options": f"-csearch_path={schema},public"}
        ).render_as_string(hide_password=False),
    )
    application = create_app(settings)
    application.state.ingestion.provider = RehearsalProvider(settings)
    research_provider = RehearsalProvider(settings)
    application.state.orchestrator.researcher.provider = research_provider
    application.state.orchestrator.researcher.search = RehearsalSearch(
        settings, research_provider, application.state.ingestion.provider
    )
    try:
        uvicorn.run(
            application,
            host="0.0.0.0",
            port=8000,
            access_log=False,
            log_level="warning",
        )
    finally:
        if os.environ.get("UI_PRESERVE_SCHEMA") != "1":
            with admin.begin() as connection:
                connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


if __name__ == "__main__":
    main()
