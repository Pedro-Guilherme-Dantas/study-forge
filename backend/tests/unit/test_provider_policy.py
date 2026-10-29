import pytest
from pydantic import ValidationError
from app.providers.gemini import GeminiProvider
from app.settings import Settings
from app.errors import AppError


@pytest.mark.unit
async def test_fixture_vectors_are_deterministic_finite_and_normalized():
    import math

    provider = GeminiProvider(Settings())
    first = await provider.embed(["Fotossíntese e energia solar", ""])
    second = await provider.embed(["Fotossíntese e energia solar", ""])
    assert first == second and len(first[0]) == 768
    assert all(math.isfinite(x) for vector in first for x in vector)
    assert abs(sum(x * x for x in first[0]) - 1) < 1e-6


@pytest.mark.unit
@pytest.mark.parametrize(
    "flag", ["langsmith_tracing", "langchain_tracing_v2", "log_payloads"]
)
def test_tracing_cannot_be_enabled(flag):
    with pytest.raises(ValidationError):
        Settings(**{flag: True})


@pytest.mark.unit
@pytest.mark.parametrize("vector", [[0.0] * 768, [1.0] * 3, [float("nan")] * 768])
def test_invalid_vectors_rejected(vector):
    with pytest.raises(AppError):
        GeminiProvider.validate_vector(vector)


@pytest.mark.unit
def test_missing_credentials_are_reported_before_client_factory():
    calls = []
    provider = GeminiProvider(
        Settings(app_mode="real"), client_factory=lambda: calls.append("called")
    )
    with pytest.raises(AppError) as failure:
        provider._client()
    assert failure.value.code == "PROVIDER_NOT_CONFIGURED"
    assert calls == []


@pytest.mark.unit
@pytest.mark.parametrize("backend", ["developer", "vertex"])
def test_configured_provider_needs_no_retention_receipt(backend):
    sentinel = object()
    settings = Settings(
        app_mode="real",
        gemini_backend=backend,
        gemini_api_key="synthetic-test-key",
        gemini_project="test-project",
        gemini_location="test-region",
    )
    provider = GeminiProvider(settings, client_factory=lambda: sentinel)
    assert provider._client() is sentinel
