import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings


@pytest.fixture
def client():
    with TestClient(create_app(Settings()), base_url="http://127.0.0.1:8000") as client:
        yield client


def bootstrap(client):
    result = client.post("/api/sessions", headers={"Origin": "http://127.0.0.1:8000"})
    assert result.status_code == 201
    return {
        "Origin": "http://127.0.0.1:8000",
        "X-CSRF-Token": result.json()["csrf_token"],
    }


@pytest.mark.contract
def test_origin_host_and_csrf_guard_even_multipart(client):
    assert (
        client.get("/api/runtime", headers={"Host": "evil.example"}).status_code == 403
    )
    assert (
        client.post(
            "/api/sessions", headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    headers = bootstrap(client)
    assert client.post("/api/conversations").status_code == 403
    assert (
        client.post(
            "/api/conversations", headers={**headers, "X-CSRF-Token": "bad"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/materials",
            headers={"Origin": "https://evil.example"},
            files={"file": ("a.md", b"marker")},
        ).status_code
        == 403
    )
    assert (
        "access-control-allow-origin"
        not in client.get(
            "/api/runtime", headers={"Origin": "https://evil.example"}
        ).headers
    )


@pytest.mark.contract
def test_bootstrap_cookie_public_config_and_headers(client):
    headers = bootstrap(client)
    cookie = client.cookies.get("sf_session")
    assert cookie
    response = client.get("/api/runtime")
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["provider"]["retention_status"] == "fixture_only"
    assert "api_key" not in response.text
    assert response.json()["limits"]["embedding_dimensions"] == 768
    assert "default-src 'self'" in response.headers["content-security-policy"]
