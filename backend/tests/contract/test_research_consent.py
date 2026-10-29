import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from app.main import create_app
from app.settings import Settings
from tests.support import headers
from tests.support import wait_turn


@pytest.mark.contract
def test_offer_wait_decline_and_explicit_request(library_url):
    app = create_app(Settings(database_url=library_url))
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        base = f"/api/conversations/{conversation}"
        turn = client.post(
            base + "/turns", headers=auth, json={"message": "Explique célula"}
        ).json()
        value = wait_turn(client, conversation, turn["turn_id"])
        session = next(iter(app.state.store._sessions.values()))
        assert (
            session.conversation.research == {} and session.conversation.sources == {}
        )
        offer = str(value["research_offer"]["offer_id"])
        result = client.post(
            base + f"/research-offers/{offer}/decision",
            headers=auth,
            json={"accept": False},
        )
        assert result.status_code == 200 and result.json()["state"] == "declined"
        assert (
            session.conversation.research == {} and session.conversation.sources == {}
        )
        turn = client.post(
            base + "/turns",
            headers=auth,
            json={"message": "Pesquise na web sobre células"},
        ).json()
        value = wait_turn(client, conversation, turn["turn_id"])
        assert value["research_offer"] is None and value["research_id"] is not None, (
            value
        )
        research = client.get(base + "/research/" + value["research_id"]).json()
        assert research["status"] == "succeeded", research
        assert len(research["sources"]) == 2
        assert value["citations"] and value["citations"][0]["scope"] == "temporary"
        source = client.get(
            base + "/sources/" + research["sources"][0]["source_id"]
        ).json()
        assert "célula" in source["snapshot_text"]
        engine = create_engine(library_url)
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT count(*) FROM materials")) == 0
            assert connection.scalar(text("SELECT count(*) FROM chunks")) == 0
        engine.dispose()
        client.delete(base, headers=auth)
        assert session.conversation is None
        assert (
            client.get(
                base + "/sources/" + research["sources"][0]["source_id"]
            ).status_code
            == 410
        )


@pytest.mark.contract
def test_accept_offer_is_idempotent(library_url):
    app = create_app(Settings(database_url=library_url))
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        conversation = client.post("/api/conversations", headers=auth).json()[
            "conversation_id"
        ]
        base = f"/api/conversations/{conversation}"
        turn = client.post(
            base + "/turns", headers=auth, json={"message": "Explique célula"}
        ).json()
        value = wait_turn(client, conversation, turn["turn_id"])
        path = (
            base
            + "/research-offers/"
            + value["research_offer"]["offer_id"]
            + "/decision"
        )
        first = client.post(path, headers=auth, json={"accept": True})
        assert first.status_code == 202 and first.json()["research_id"]
        second = client.post(path, headers=auth, json={"accept": True})
        assert second.json()["research_id"] == first.json()["research_id"]
        value = wait_turn(client, conversation, turn["turn_id"])
        assert value["status"] != "failed", value
        assert (
            len(next(iter(app.state.store._sessions.values())).conversation.research)
            == 1
        )
