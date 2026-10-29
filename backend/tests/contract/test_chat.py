from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings
from tests.support import headers, wait_for_operation, wait_turn


@pytest.mark.contract
def test_tutor_citations_close_and_restart(library_url):
    with TestClient(
        create_app(Settings(database_url=library_url)), base_url="http://127.0.0.1:8000"
    ) as client:
        auth = headers(client)
        uploaded = client.post(
            "/api/materials",
            headers=auth,
            files={
                "file": (
                    "celula.md",
                    "# Célula\n\nA célula é a unidade básica dos seres vivos.".encode(),
                )
            },
        ).json()
        assert (
            wait_for_operation(client, uploaded["operation_id"])["state"] == "succeeded"
        )
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        turn = client.post(
            f"/api/conversations/{conversation}/turns",
            headers=auth,
            json={"message": "Explique célula"},
        ).json()
        result = wait_turn(client, conversation, turn["turn_id"])
        assert (
            result["evidence_status"] == "partial"
        )  # fixture never claims semantic sufficiency
        citation = result["citations"][0]
        assert citation["scope"] == "library" and "célula" in citation["quote"]
        path = f"/api/conversations/{conversation}/citations/{citation['citation_id']}"
        assert client.get(path).json() == citation
        assert (
            client.get(
                f"/api/conversations/{uuid4()}/turns/{turn['turn_id']}"
            ).status_code
            == 410
        )
        assert (
            client.delete(
                f"/api/conversations/{conversation}", headers=auth
            ).status_code
            == 204
        )
        assert client.get(path).status_code == 410
        new_id = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        assert new_id != conversation
        assert len(client.get("/api/materials").json()["items"]) == 1


@pytest.mark.contract
def test_absence_of_evidence_has_offer_and_no_external_call(library_url):
    app = create_app(Settings(database_url=library_url))
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        turn = client.post(
            f"/api/conversations/{conversation}/turns",
            headers=auth,
            json={"message": "O que é gravidade?"},
        ).json()
        result = wait_turn(client, conversation, turn["turn_id"])
        assert result["status"] == "awaiting_research_consent"
        assert result["citations"] == [] and result["evidence_status"] == "insufficient"
        session = next(iter(app.state.store._sessions.values()))
        assert (
            session.conversation.research == {} and session.conversation.sources == {}
        )


@pytest.mark.contract
def test_turn_admission_rejects_parallel_and_oversize(library_url):
    import asyncio

    class WaitingGraph:
        async def ainvoke(self, *args, **kwargs):
            await asyncio.Event().wait()

    app = create_app(Settings(database_url=library_url, max_message_bytes=20))
    app.state.orchestrator.graph = WaitingGraph()
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        path = f"/api/conversations/{conversation}/turns"
        assert (
            client.post(path, headers=auth, json={"message": "a" * 21}).status_code
            == 413
        )
        assert (
            client.post(path, headers=auth, json={"message": "Pergunta"}).status_code
            == 202
        )
        assert (
            client.post(path, headers=auth, json={"message": "Outra"}).status_code
            == 409
        )
        client.delete(f"/api/conversations/{conversation}", headers=auth)
        assert app.state.executor.pending == 0
