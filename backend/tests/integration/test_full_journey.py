import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings
from tests.support import headers, wait_for_operation
from tests.support import wait_turn


@pytest.mark.integration
def test_local_fixture_journey_all_five_stories_and_restart(library_url):
    settings = Settings(database_url=library_url)
    with TestClient(create_app(settings), base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        upload = client.post(
            "/api/materials",
            headers=auth,
            files={
                "file": (
                    "local.md",
                    "# Célula\n\nA célula é a unidade básica da vida.".encode(),
                )
            },
        ).json()
        assert (
            wait_for_operation(client, upload["operation_id"])["state"] == "succeeded"
        )
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        base = f"/api/conversations/{conversation}"
        turn = client.post(
            base + "/turns", headers=auth, json={"message": "Explique célula"}
        ).json()
        result = wait_turn(client, conversation, turn["turn_id"])
        assert result["citations"][0]["scope"] == "library"
        offer = result["research_offer"]["offer_id"]
        assert (
            client.post(
                base + f"/research-offers/{offer}/decision",
                headers=auth,
                json={"accept": False},
            ).status_code
            == 200
        )
        assert client.get("/api/progress").json()["research"] == []
        turn = client.post(
            base + "/turns",
            headers=auth,
            json={"message": "Pesquise na web sobre células"},
        ).json()
        result = wait_turn(client, conversation, turn["turn_id"])
        research = client.get(base + "/research/" + result["research_id"]).json()
        chosen = research["sources"][0]
        source = client.get(base + "/sources/" + chosen["source_id"]).json()
        assert source["temporary"] is True
        selected = client.post(
            base + "/sources/" + chosen["source_id"] + "/selection",
            headers=auth,
            json={"snapshot_hash": chosen["snapshot_hash"]},
        ).json()
        assert (
            wait_for_operation(client, selected["operation_id"])["state"] == "succeeded"
        )
        assert len(client.get("/api/progress").json()["materials"]) == 2
        client.delete(base, headers=auth)
        assert client.get(base + "/sources/" + chosen["source_id"]).status_code == 410
        assert client.get("/api/progress").json()["research"] == []
    with TestClient(create_app(settings), base_url="http://127.0.0.1:8000") as client:
        headers(client)
        assert len(client.get("/api/materials").json()["items"]) == 2
        assert client.get("/api/progress").json()["research"] == []
