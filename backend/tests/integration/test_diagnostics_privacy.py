import logging
import pytest
from app.diagnostics import event
from app.main import create_app
from app.settings import Settings
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_logs_are_allowlisted_and_unexpected_errors_are_sanitized(caplog):
    with caplog.at_level(logging.INFO, logger="studyforge"):
        event(
            stage="request",
            status=500,
            prompt="PRIVATE_MARKER",
            response="PRIVATE_MARKER",
        )
    assert "PRIVATE_MARKER" not in caplog.text
    app = create_app(Settings())

    @app.get("/test-error")
    async def fail():
        raise RuntimeError("PRIVATE_MARKER secret")

    app.router.routes.insert(0, app.router.routes.pop())
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        response = client.get("/test-error")
    assert response.status_code == 500
    assert "PRIVATE_MARKER" not in response.text
    assert "PRIVATE_MARKER" not in caplog.text
