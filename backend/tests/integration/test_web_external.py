"""Opt-in real Brave/HTML/Gemini journey in a disposable PostgreSQL schema."""

import os
import time
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings
from tests.support import headers

pytestmark = [
    pytest.mark.external,
    pytest.mark.skipif(
        os.getenv("RUN_EXTERNAL_TESTS") != "1",
        reason="Explicit external experiment required",
    ),
]


def wait_terminal(client, path, field, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = client.get(path).json()
        if value[field] not in ("running", "queued"):
            return value
        time.sleep(0.5)
    pytest.fail("External journey exceeded its deadline")


def test_brave_html_temporary_tutor_explicit_selection_and_close(library_url):
    settings = Settings(
        app_mode="real", database_url=library_url, max_pages_per_research=1
    )
    if (
        not settings.search_api_key.get_secret_value()
        or not settings.gemini_api_key.get_secret_value()
    ):
        pytest.skip("External credentials missing")
    app = create_app(settings)
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        base = f"/api/conversations/{conversation}"
        turn = client.post(
            base + "/turns",
            headers=auth,
            json={
                "message": "site:docs.python.org/pt-br/3/tutorial/controlflow.html Em Python, quando a cláusula else de um laço é executada e como break interfere?",
                "intent": "research",
            },
        ).json()
        result = wait_terminal(client, base + "/turns/" + turn["turn_id"], "status", 70)
        research = client.get(base + "/research/" + result["research_id"]).json()
        print(
            {
                "research_status": research["status"],
                "available_sources": sum(
                    source["state"] == "available" for source in research["sources"]
                ),
                "error_codes": research["error_codes"],
                "turn_status": result["status"],
            }
        )
        assert research["status"] in ("succeeded", "partial"), research["error_codes"]
        assert result["status"] != "failed", result.get("error", {})
        assert result["citations"] and all(
            c["scope"] == "temporary" for c in result["citations"]
        )
        assert client.get("/api/materials").json()["items"] == []
        source = next(
            source for source in research["sources"] if source["state"] == "available"
        )
        detail = client.get(base + "/sources/" + source["source_id"]).json()
        assert len(detail["snapshot_text"]) > 1000
        selected = client.post(
            base + "/sources/" + source["source_id"] + "/selection",
            headers=auth,
            json={"snapshot_hash": source["snapshot_hash"]},
        ).json()
        client.delete(base, headers=auth)
        assert client.get(base + "/sources/" + source["source_id"]).status_code == 410
        operation = wait_terminal(
            client, "/api/operations/" + selected["operation_id"], "state", 125
        )
        assert operation["state"] == "succeeded", operation["error_code"]
        assert len(client.get("/api/materials").json()["items"]) == 1
        assert client.get("/api/progress").json()["research"] == []
