"""HTTP journey against an isolated PostgreSQL schema; no browser or external upload."""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings
from tests.contract.test_materials import headers, wait_for_operation


@pytest.mark.integration
def test_uploaded_library_survives_application_restart(library_url):
    settings = Settings(database_url=library_url)
    with TestClient(create_app(settings), base_url="http://127.0.0.1:8000") as client:
        auth = headers(client)
        receipt = client.post(
            "/api/materials",
            headers=auth,
            files={
                "file": (
                    "journey.md",
                    b"# Journey\n\nOwn synthetic Markdown.",
                    "application/pdf",
                )
            },
        ).json()
        assert (
            wait_for_operation(client, receipt["operation_id"])["state"] == "succeeded"
        )
        instance = client.get("/api/runtime").json()["server_instance_id"]
    with TestClient(create_app(settings), base_url="http://127.0.0.1:8000") as client:
        headers(client)
        assert client.get("/api/runtime").json()["server_instance_id"] != instance
        material = client.get("/api/materials/" + receipt["material_id"]).json()
        assert material["material"]["active_version_id"] == receipt["version_id"]
        assert (
            client.get("/api/operations/" + receipt["operation_id"]).json()["state"]
            == "succeeded"
        )
