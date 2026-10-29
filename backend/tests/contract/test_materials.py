import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings
from tests.support import headers, wait_for_operation


@pytest.mark.contract
def test_empty_invalid_and_valid_library(library_url):
    with TestClient(
        create_app(Settings(database_url=library_url)), base_url="http://127.0.0.1:8000"
    ) as client:
        auth = headers(client)
        assert client.get("/api/materials").json()["items"] == []
        for name, value in [
            ("bad.pdf", b"hello"),
            ("empty.md", b""),
            ("bad.md", b"\x00"),
        ]:
            assert (
                client.post(
                    "/api/materials", headers=auth, files={"file": (name, value)}
                ).status_code
                == 422
            )
        receipt = client.post(
            "/api/materials",
            headers=auth,
            files={
                "file": (
                    "Biologia.md",
                    "# Biologia\n\nA célula é a unidade básica da vida.".encode(),
                )
            },
        )
        assert receipt.status_code == 202, receipt.text
        operation = wait_for_operation(client, receipt.json()["operation_id"])
        assert operation["state"] == "succeeded", operation
        items = client.get("/api/materials").json()["items"]
        assert len(items) == 1 and items[0]["status"] == "ready"
        detail = client.get("/api/materials/" + items[0]["material_id"]).json()
        version = detail["material"]["active_version_id"]
        chunks = client.get(
            f"/api/materials/{items[0]['material_id']}/versions/{version}/chunks"
        ).json()["items"]
        assert chunks and "célula" in chunks[0]["text"]
        read = client.get(
            f"/api/materials/{items[0]['material_id']}/versions/{version}/chunks/{chunks[0]['chunk_id']}"
        )
        assert (
            read.status_code == 200
            and read.json()["locator"]["kind"] == "markdown_original"
        )
        from uuid import uuid4

        wrong_owner = client.get(
            f"/api/materials/{uuid4()}/versions/{version}/chunks/{chunks[0]['chunk_id']}"
        )
        assert wrong_owner.status_code == 404
        assert (
            client.post(
                "/api/operations/" + operation["operation_id"] + "/retry", headers=auth
            ).status_code
            == 409
        )


@pytest.mark.contract
def test_upload_size_and_associations(library_url):
    with TestClient(
        create_app(Settings(database_url=library_url, max_upload_bytes=10)),
        base_url="http://127.0.0.1:8000",
    ) as client:
        auth = headers(client)
        result = client.post(
            "/api/materials", headers=auth, files={"file": ("a.md", b"x" * 11)}
        )
        assert result.status_code == 413
        assert client.get("/api/materials").json()["items"] == []
