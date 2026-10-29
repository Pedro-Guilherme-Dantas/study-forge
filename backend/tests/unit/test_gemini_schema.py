from types import SimpleNamespace
import pytest
from app.providers.gemini import GeminiProvider
from app.settings import Settings
from app.agents.tutor import TutorOutput


async def test_generation_sends_json_schema_without_proto_additional_properties():
    class Models:
        async def generate_content(self, **kwargs):
            config = kwargs["config"]
            assert config.response_schema is None
            assert config.response_json_schema["additionalProperties"] is False
            return SimpleNamespace(
                text='{"answer_markdown":"Não há evidência.","evidence_status":"insufficient"}',
                usage_metadata=None,
                model_version="test-only",
            )

    class AsyncClient:
        models = Models()

        async def aclose(self):
            pass

    provider = GeminiProvider(
        Settings(app_mode="real", gemini_api_key="synthetic-key"),
        client_factory=lambda: SimpleNamespace(aio=AsyncClient()),
    )
    output = await provider.generate("Synthetic fixture", TutorOutput)
    assert output.evidence_status == "insufficient"


async def test_failed_generation_does_not_reuse_previous_token_usage():
    from app.errors import AppError

    class Models:
        async def generate_content(self, **kwargs):
            raise RuntimeError("synthetic failure")

    class AsyncClient:
        models = Models()

        async def aclose(self):
            pass

    provider = GeminiProvider(
        Settings(app_mode="real", gemini_api_key="synthetic-key"),
        client_factory=lambda: SimpleNamespace(aio=AsyncClient()),
    )
    provider.last_generation_metadata = {"usage": {"total_token_count": 999}}
    with pytest.raises(AppError):
        await provider.generate("Synthetic fixture", TutorOutput)
    assert "usage" not in provider.last_generation_metadata
    assert provider.last_generation_metadata["error_type"] == "RuntimeError"


@pytest.mark.parametrize("status,expected_calls", [(503, 2), (400, 1), (403, 1)])
async def test_only_transient_errors_retry_and_all_attempts_count(
    status, expected_calls, monkeypatch
):
    from app.providers.gemini import call_provider
    from app.operations import Budget

    calls = []

    class Failure(Exception):
        code = status

    async def fail():
        calls.append(1)
        raise Failure()

    async def no_wait(*args):
        pass

    monkeypatch.setattr("app.providers.gemini.asyncio.sleep", no_wait)
    budget = Budget(5, attempts=4)
    with pytest.raises(Failure):
        await call_provider(budget, fail)
    assert len(calls) == expected_calls and budget.attempts == 4 - expected_calls


async def test_retry_after_is_respected_within_budget(monkeypatch):
    from app.providers.gemini import call_provider
    from app.operations import Budget

    delays = []
    calls = []

    class Failure(Exception):
        code = 429
        details = {
            "error": {
                "details": [
                    {
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "3s",
                    }
                ]
            }
        }

    async def action():
        calls.append(1)
        if len(calls) == 1:
            raise Failure()
        return "ok"

    async def wait(seconds):
        delays.append(seconds)

    monkeypatch.setattr("app.providers.gemini.asyncio.sleep", wait)
    assert await call_provider(Budget(10), action) == "ok" and delays == [3]


async def test_retry_after_beyond_deadline_does_not_wait_or_retry(monkeypatch):
    from app.providers.gemini import call_provider
    from app.operations import Budget

    class Failure(Exception):
        code = 429
        details = {
            "error": {
                "details": [
                    {
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "60s",
                    }
                ]
            }
        }

    async def action():
        raise Failure()

    async def forbidden(*args):
        pytest.fail("Must not wait beyond deadline")

    monkeypatch.setattr("app.providers.gemini.asyncio.sleep", forbidden)
    budget = Budget(5, attempts=4)
    with pytest.raises(Failure):
        await call_provider(budget, action)
    assert budget.attempts == 3
