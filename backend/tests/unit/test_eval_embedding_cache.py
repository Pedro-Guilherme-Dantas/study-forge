from types import SimpleNamespace
import json
import pytest
from app.settings import Settings
from evals.gemini_external import embed_batch


async def test_cache_only_when_explicit_and_separates_query_task(tmp_path, monkeypatch):
    calls = []

    class Models:
        async def embed_content(self, **kwargs):
            calls.append(kwargs["config"].task_type)
            return SimpleNamespace(
                embeddings=[
                    SimpleNamespace(values=[1.0, 0.0, 0.0]) for _ in kwargs["contents"]
                ]
            )

    class Async:
        models = Models()

        async def aclose(self):
            pass

    monkeypatch.setattr(
        "app.providers.gemini.GeminiProvider._client",
        lambda self: SimpleNamespace(aio=Async()),
    )
    settings = Settings(embedding_batch_size=1)
    first = await embed_batch(settings, ["authored public fixture"], 3, False, tmp_path)
    assert (
        await embed_batch(settings, ["authored public fixture"], 3, False, tmp_path)
        == first
    )
    assert len(calls) == 1
    await embed_batch(settings, ["authored public fixture"], 3, True, tmp_path)
    assert calls == ["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]
    for file in tmp_path.glob("*.json"):
        file.write_text(json.dumps([float("nan")] * 3))
    with pytest.raises(ValueError):
        await embed_batch(settings, ["authored public fixture"], 3, False, tmp_path)
