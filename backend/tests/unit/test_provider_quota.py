from types import SimpleNamespace
import pytest
from app.providers.gemini import GeminiProvider
from app.agents.tutor import TutorOutput
from app.settings import Settings
from app.errors import AppError


@pytest.mark.parametrize("stage", ["embed", "generation"])
@pytest.mark.parametrize("daily", [True, False])
async def test_provider_quota_is_actionable_without_exposing_provider_payload(
    stage, daily
):
    class QuotaFailure(Exception):
        code = 429
        details = {
            "error": {
                "message": "PRIVATE_PROVIDER_PAYLOAD",
                "details": [
                    {
                        "violations": [
                            {
                                "quotaId": "RequestsPerDay"
                                if daily
                                else "RequestsPerMinute"
                            }
                        ]
                    },
                    {"@type": "google.rpc.RetryInfo", "retryDelay": "9999s"},
                ],
            }
        }

    class Models:
        async def embed_content(self, **kwargs):
            raise QuotaFailure("PRIVATE_PROVIDER_PAYLOAD")

        async def generate_content(self, **kwargs):
            raise QuotaFailure("PRIVATE_PROVIDER_PAYLOAD")

    class Client:
        models = Models()

        async def aclose(self):
            pass

    provider = GeminiProvider(
        Settings(app_mode="real", gemini_api_key="synthetic-key"),
        client_factory=lambda: SimpleNamespace(aio=Client()),
    )
    with pytest.raises(AppError) as failure:
        if stage == "embed":
            await provider.embed(["Authored diagnostic text"])
        else:
            await provider.generate("Authored diagnostic question", TutorOutput)
    assert failure.value.code == "PROVIDER_QUOTA_EXCEEDED"
    assert failure.value.status == 429
    assert ("diária" in failure.value.message) == daily
    assert "PRIVATE_PROVIDER_PAYLOAD" not in str(failure.value.envelope())
