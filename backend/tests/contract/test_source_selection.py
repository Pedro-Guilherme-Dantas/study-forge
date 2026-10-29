import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from app.main import create_app
from app.settings import Settings
from tests.support import headers, wait_for_operation
from tests.support import wait_turn


@pytest.mark.contract
def test_only_selected_snapshot_is_persisted_and_duplicate_reuses_receipt(library_url):
    with TestClient(
        create_app(Settings(database_url=library_url)), base_url="http://127.0.0.1:8000"
    ) as client:
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
        sources = client.get(base + "/research/" + result["research_id"]).json()[
            "sources"
        ]
        chosen, unselected = sources
        path = base + "/sources/" + chosen["source_id"] + "/selection"
        original_cookies = dict(client.cookies)
        client.cookies.clear()
        other_auth = headers(client)
        assert (
            client.post(
                path,
                headers=other_auth,
                json={"snapshot_hash": chosen["snapshot_hash"]},
            ).status_code
            == 410
        )
        client.cookies.clear()
        client.cookies.update(original_cookies)
        assert (
            client.post(
                path, headers=auth, json={"snapshot_hash": "f" * 64}
            ).status_code
            == 409
        )
        assert (
            client.post(
                path,
                headers=auth,
                json={"snapshot_hash": chosen["snapshot_hash"], "selected": True},
            ).status_code
            == 422
        )
        receipt = client.post(
            path,
            headers={**auth, "Idempotency-Key": "test-selection-A"},
            json={"snapshot_hash": chosen["snapshot_hash"]},
        )
        assert receipt.status_code == 202, receipt.text
        duplicate = client.post(
            path, headers=auth, json={"snapshot_hash": chosen["snapshot_hash"]}
        )
        assert (
            duplicate.status_code == 200
            and duplicate.json()["operation_id"] == receipt.json()["operation_id"]
        )
        conflict = client.post(
            base + "/sources/" + unselected["source_id"] + "/selection",
            headers={**auth, "Idempotency-Key": "test-selection-A"},
            json={"snapshot_hash": unselected["snapshot_hash"]},
        )
        assert conflict.status_code == 409
        operation = wait_for_operation(client, receipt.json()["operation_id"])
        assert operation["state"] == "succeeded", operation
        detail = client.get("/api/materials/" + receipt.json()["material_id"]).json()
        chunks = client.get(
            f"/api/materials/{receipt.json()['material_id']}/versions/{receipt.json()['version_id']}/chunks"
        ).json()["items"]
        assert chunks and chunks[0]["locator"]["kind"] == "html_extracted_snapshot"
        assert detail["origin_url"] == chosen["origin_url"]
        engine = create_engine(library_url)
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT count(*) FROM selection_grants")) == 1
            urls = (
                connection.execute(text("SELECT original_url FROM materials"))
                .scalars()
                .all()
            )
            assert (
                urls == [chosen["origin_url"]] and unselected["origin_url"] not in urls
            )
        engine.dispose()
        client.delete(base, headers=auth)
        assert (
            client.post(
                path, headers=auth, json={"snapshot_hash": chosen["snapshot_hash"]}
            ).status_code
            == 410
        )
        assert len(client.get("/api/materials").json()["items"]) == 1
