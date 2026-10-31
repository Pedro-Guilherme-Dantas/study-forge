"""Explicit opt-in: authored data only; secrets stay inside the container environment."""

import os
import time
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings
from tests.support import headers, wait_for_operation

pytestmark = [
    pytest.mark.external,
    pytest.mark.skipif(
        os.getenv("RUN_EXTERNAL_TESTS") != "1",
        reason="Explicit external experiment required",
    ),
]


def test_real_gemini_markdown_to_retrieval_tutor_and_citation(library_url):
    settings = Settings(app_mode="real", database_url=library_url)
    if not settings.gemini_api_key.get_secret_value():
        pytest.skip("Gemini credentials not configured")
    with TestClient(create_app(settings), base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        uploaded = client.post(
            "/api/materials",
            headers=auth,
            files={
                "file": (
                    "real-eval.md",
                    "# Célula\n\nA célula é a unidade básica da vida. A membrana celular delimita a célula.".encode(),
                )
            },
        ).json()
        for _ in range(120):
            operation = client.get("/api/operations/" + uploaded["operation_id"]).json()
            if operation["state"] not in ("queued", "running"):
                break
            time.sleep(0.5)
        assert operation["state"] == "succeeded", operation.get("error_code")
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        base = f"/api/conversations/{conversation}"
        turn = client.post(
            base + "/turns",
            headers=auth,
            json={"message": "Segundo o material, o que é uma célula?"},
        ).json()
        for _ in range(130):
            result = client.get(base + "/turns/" + turn["turn_id"]).json()
            if result["status"] != "running":
                break
            time.sleep(0.5)
        assert result["status"] != "failed", result.get("error", {})
        assert result["evidence_status"] in ("supported", "partial")
        assert result["citations"] and all(
            c["scope"] == "library" for c in result["citations"]
        )
        assert "unidade básica" in result["answer_markdown"].casefold()
        reference = result["citations"][0]
        assert "A célula é a unidade básica da vida." in reference["quote"]
        assert (
            client.get(base + "/citations/" + reference["citation_id"]).status_code
            == 200
        )
        client.delete(base, headers=auth)
        assert (
            client.get(base + "/citations/" + reference["citation_id"]).status_code
            == 410
        )
        if settings.studyforge_tracing:
            # Keep the isolated test server alive until its authorized trace is exported.
            client.portal.call(app_trace_flush, client.app.state.observability)


async def app_trace_flush(observability):
    import asyncio

    await asyncio.wait_for(observability.flush(), 15)
    assert observability.status()["failed"] == 0
