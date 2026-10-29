"""Shared integration setup; never import one test module from another for setup."""

import time
import pytest
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


def headers(client):
    value = client.post(
        "/api/sessions", headers={"Origin": "http://127.0.0.1:8000"}
    ).json()
    return {"Origin": "http://127.0.0.1:8000", "X-CSRF-Token": value["csrf_token"]}


def wait_for_operation(client, operation_id):
    for _ in range(100):
        response = client.get("/api/operations/" + operation_id)
        assert response.status_code == 200, response.text
        value = response.json()
        if value["state"] not in ("queued", "running"):
            return value
        time.sleep(0.03)
    pytest.fail("Ingestion did not reach a terminal state")


def wait_turn(client, conversation, turn):
    for _ in range(100):
        response = client.get(f"/api/conversations/{conversation}/turns/{turn}")
        assert response.status_code == 200, response.text
        value = response.json()
        if value["status"] != "running":
            return value
        time.sleep(0.03)
    pytest.fail("Turn did not finish")


async def prepare_research_session(url):
    from app.agents.researcher import Researcher
    from app.providers.search import SearchProvider
    from app.web_fetch import SafeFetcher
    from app.operations import Budget
    from app.sessions import SessionStore

    engine, database, executor, ingestion = service_for(url)
    researcher = Researcher(
        ingestion.settings,
        SearchProvider(ingestion.settings),
        SafeFetcher(ingestion.settings),
        ingestion.provider,
    )
    snapshots, _, _ = await researcher.collect("fixture", Budget(5))
    store = SessionStore()
    session = store.create_session()
    conversation = store.create_conversation(session)
    for snapshot in snapshots:
        conversation.sources[str(snapshot.summary.source_id)] = snapshot
    return (
        engine,
        database,
        executor,
        ingestion,
        store,
        session,
        conversation,
        snapshots,
    )
