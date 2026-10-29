import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings
from app.providers.gemini import GeminiProvider
from app.errors import AppError
from tests.support import headers
from tests.support import wait_turn


@pytest.mark.integration
@pytest.mark.parametrize("scenario", ["empty", "partial", "quota", "not_configured"])
def test_research_failures_are_visible_without_simulated_success(library_url, scenario):
    settings = Settings(
        database_url=library_url,
        app_mode="real" if scenario == "not_configured" else "fixture",
        max_temporary_sources=1 if scenario == "quota" else 20,
    )
    app = create_app(settings)

    class EmptySearch:
        async def discover(self, *args):
            return []

    class FailsFirstEmbedding(GeminiProvider):
        calls = 0

        async def embed(self, texts, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise AppError(
                    "SOURCE_UNAVAILABLE", "Fonte de ensaio indisponível.", 502, "embed"
                )
            return await super().embed(texts, **kwargs)

    if scenario == "empty":
        app.state.orchestrator.researcher.search = EmptySearch()
    if scenario == "partial":
        app.state.orchestrator.researcher.provider = FailsFirstEmbedding(settings)
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        base = f"/api/conversations/{conversation}"
        turn = client.post(
            base + "/turns",
            headers=auth,
            json={"message": "Pesquise na web sobre células"},
        ).json()
        result = wait_turn(client, conversation, turn["turn_id"])
        research = client.get(base + "/research/" + result["research_id"]).json()
        assert research["status"] != "running"
        if scenario == "empty":
            assert research["status"] == "empty" and result["citations"] == []
        elif scenario == "partial":
            assert research["status"] == "partial"
            assert sorted(source["state"] for source in research["sources"]) == [
                "available",
                "unavailable",
            ]
            available = {
                source["source_id"]
                for source in research["sources"]
                if source["state"] == "available"
            }
            assert all(
                citation["source_id"] in available for citation in result["citations"]
            )
        else:
            assert result["status"] == "failed" and research["status"] == "failed"
            expected = (
                "EXECUTION_LIMIT" if scenario == "quota" else "SEARCH_NOT_CONFIGURED"
            )
            assert result["error"]["error"]["code"] == expected
        assert client.get("/api/materials").json()["items"] == []
        client.delete(base, headers=auth)
        assert (
            client.get(base + "/research/" + result["research_id"]).status_code == 410
        )
