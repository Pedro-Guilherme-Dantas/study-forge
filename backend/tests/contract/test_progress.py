import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings
from tests.support import headers, wait_for_operation
from tests.support import wait_turn


@pytest.mark.contract
def test_operational_progress_research_discard_and_library_preserved(library_url):
    with TestClient(
        create_app(Settings(database_url=library_url)), base_url="http://127.0.0.1:8000"
    ) as client:
        auth = headers(client)
        upload = client.post(
            "/api/materials",
            headers=auth,
            files={"file": ("own.md", b"# Own\n\nOwn text.")},
        ).json()
        wait_for_operation(client, upload["operation_id"])
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        turn = client.post(
            f"/api/conversations/{conversation}/turns",
            headers=auth,
            json={"message": "Pesquise na web sobre células"},
        ).json()
        wait_turn(client, conversation, turn["turn_id"])
        snapshot = client.get("/api/progress").json()
        assert set(snapshot) == {"materials", "ingestions", "research"}
        assert (
            len(snapshot["research"]) == 1
            and snapshot["ingestions"][0]["state"] == "succeeded"
        )
        client.delete(f"/api/conversations/{conversation}", headers=auth)
        snapshot = client.get("/api/progress").json()
        assert snapshot["research"] == [] and len(snapshot["materials"]) == 1
