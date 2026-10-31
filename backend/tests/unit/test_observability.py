import asyncio
import json

import pytest
from pydantic import ValidationError

from app.errors import AppError
from app.settings import Settings
from app.observability import Observability, span, annotate


@pytest.mark.unit
async def test_detailed_capture_includes_content_but_redacts_backend_secrets():
    from app.observability import capture_content

    settings = Settings(
        studyforge_tracing=True,
        studyforge_trace_content=True,
        langsmith_api_key="synthetic-langsmith-secret",
        gemini_api_key="synthetic-gemini-secret",
        search_api_key="synthetic-search-secret",
    )
    sink = Sink()
    tracing = Observability(settings, client=sink)
    await tracing.start()
    with tracing.turn("content-turn", "fixture"):
        capture_content(inputs={"question": "Explique célula synthetic-gemini-secret"})
        with span("tutor"):
            capture_content(
                inputs={"question": "célula", "api_key": "synthetic-langsmith-secret"},
                outputs={"answer_markdown": "A célula é a unidade básica."},
            )
    await tracing.flush()
    await tracing.close()
    assert sink.runs[0]["inputs"]["question"] == "Explique célula [REDACTED]"
    assert sink.runs[1]["outputs"]["answer_markdown"].startswith("A célula")
    serialized = json.dumps(sink.runs, default=str)
    assert "synthetic-gemini-secret" not in serialized
    assert "synthetic-langsmith-secret" not in serialized
    assert sink.runs[0]["extra"]["metadata"]["capture"] == "content"


@pytest.mark.unit
async def test_metadata_mode_never_captures_explicit_content():
    from app.observability import capture_content

    sink = Sink()
    tracing = Observability(configured(), client=sink)
    await tracing.start()
    with tracing.turn("metadata-turn", "fixture"):
        capture_content(inputs={"question": "PRIVATE"}, outputs={"answer": "PRIVATE"})
    await tracing.flush()
    await tracing.close()
    assert "PRIVATE" not in json.dumps(sink.runs, default=str)


@pytest.mark.unit
async def test_detailed_demo_shows_question_retrieved_text_and_answer():
    from evals.trace_demo import run_demo

    runs = await run_demo(offline=True, content=True)
    roots = [run for run in runs if run["parent_run_id"] is None]
    assert any(run["inputs"].get("question") == "Explique célula" for run in roots)
    assert any("unidade básica" in run["outputs"].get("answer", "") for run in roots)
    retrieval = next(
        run
        for run in runs
        if run["name"] == "retrieve" and run["outputs"].get("count") == 1
    )
    assert retrieval["outputs"]["documents"][0]["page_content"].startswith("A célula")
    assert retrieval["outputs"]["documents"][0]["metadata"]["distance"] == 0.1
    assert any(
        run["outputs"].get("answer_markdown") for run in runs if run["name"] == "tutor"
    )


@pytest.mark.unit
async def test_generation_span_captures_actual_prompt_response_and_usage():
    from types import SimpleNamespace
    from app.agents.tutor import TutorOutput
    from app.providers.gemini import GeminiProvider

    class FakeClient:
        def __init__(self):
            self.aio = self
            self.models = self

        async def generate_content(self, **kwargs):
            assert "provider-secret" in kwargs["contents"]
            return SimpleNamespace(
                text=json.dumps(
                    {
                        "answer_markdown": "Resposta real do contrato",
                        "evidence_status": "insufficient",
                    }
                ),
                usage_metadata=SimpleNamespace(
                    prompt_token_count=12,
                    candidates_token_count=8,
                    total_token_count=20,
                ),
                model_version="test-model",
                candidates=[],
            )

        async def aclose(self):
            pass

    settings = Settings(
        app_mode="real",
        studyforge_tracing=True,
        studyforge_trace_content=True,
        langsmith_api_key="ls-secret",
        gemini_api_key="provider-secret",
    )
    sink = Sink()
    tracing = Observability(settings, client=sink)
    await tracing.start()
    with tracing.turn("generation", "real"):
        result = await GeminiProvider(settings, client_factory=FakeClient).generate(
            "Pergunta provider-secret", TutorOutput
        )
    await tracing.flush()
    await tracing.close()
    generation = next(run for run in sink.runs if run["name"] == "gemini.generate")
    assert generation["inputs"]["messages"][0]["content"] == "Pergunta [REDACTED]"
    assert (
        "Resposta real do contrato" in generation["outputs"]["generations"][0]["text"]
    )
    assert generation["outputs"]["total_tokens"] == 20
    assert result.answer_markdown == "Resposta real do contrato"


@pytest.mark.unit
async def test_content_capture_is_bounded_and_handles_unknown_objects():
    from app.observability import capture_content

    sink = Sink()
    tracing = Observability(
        Settings(
            studyforge_tracing=True,
            studyforge_trace_content=True,
            langsmith_api_key="synthetic-key",
        ),
        client=sink,
    )
    await tracing.start()
    with tracing.turn("large", "fixture"):
        capture_content(inputs={"question": "á" * 100000, "unknown": object()})
        for _ in range(30):
            with span("tutor"):
                capture_content(outputs={"answer": "á" * 100000})
    await tracing.flush()
    await tracing.close()
    assert len(json.dumps(sink.runs, default=str, ensure_ascii=False).encode()) < 600000
    assert "[TRUNCATED]" in json.dumps(sink.runs, default=str)
    assert sink.runs[0]["inputs"]["unknown"] == "[NOT_CAPTURED]"


class Sink:
    def __init__(self, fail=False):
        self.runs = []
        self.fail = fail

    async def create_run(self, **run):
        if self.fail:
            raise RuntimeError("secret provider response")
        self.runs.append(run)

    async def aclose(self):
        pass


def configured():
    return Settings(studyforge_tracing=True, langsmith_api_key="synthetic-key")


@pytest.mark.unit
async def test_safe_hierarchy_and_error_without_payloads():
    sink = Sink()
    tracing = Observability(configured(), client=sink)
    await tracing.start()
    with tracing.turn("turn-id", "fixture"):
        with span("retrieve", "retriever"):
            annotate(count=2, question="PRIVATE", text="PRIVATE", api_key="SECRET")
        with pytest.raises(AppError):
            with span("tutor"):
                raise AppError("INVALID_CITATION", "PRIVATE")
    await tracing.flush()
    await tracing.close()
    root, retrieve, tutor = sink.runs
    assert retrieve["parent_run_id"] == root["id"]
    assert tutor["trace_id"] == root["id"]
    assert retrieve["outputs"] == {"count": 2}
    assert tutor["error"] == "INVALID_CITATION"
    serialized = json.dumps(sink.runs, default=str)
    assert "PRIVATE" not in serialized and "SECRET" not in serialized


@pytest.mark.unit
async def test_disabled_and_export_failure_do_not_break_execution():
    sink = Sink(fail=True)
    tracing = Observability(configured(), client=sink)
    await tracing.start()
    with tracing.turn("turn-id", "fixture"):
        with span("tutor"):
            annotate(status="complete")
    await tracing.flush()
    assert tracing.status()["failed"] == 1
    assert tracing.status()["last_error_code"] == "EXPORT_FAILED"
    await tracing.close()
    disabled = Observability(Settings(), client=sink)
    with disabled.turn("turn-id", "fixture"):
        with span("tutor"):
            pass
    assert disabled.queue.empty()


@pytest.mark.unit
async def test_queue_is_bounded_and_concurrent_turns_are_isolated():
    sink = Sink()
    tracing = Observability(configured(), client=sink)

    async def turn(identifier):
        with tracing.turn(identifier, "fixture"):
            await asyncio.sleep(0)
            with span("retrieve"):
                annotate(count=1)

    await asyncio.gather(turn("one"), turn("two"))
    for index in range(20):
        with tracing.turn(str(index), "fixture"):
            pass
    assert tracing.queue.qsize() == 8
    assert tracing.status()["dropped"] == 14
    await tracing.start()
    await tracing.flush()
    roots = [run for run in sink.runs if run["parent_run_id"] is None]
    children = [run for run in sink.runs if run["parent_run_id"] is not None]
    assert len(roots) == 8
    assert {run["parent_run_id"] for run in children} == {
        roots[0]["id"],
        roots[1]["id"],
    }
    await tracing.close()


@pytest.mark.unit
def test_tracing_requires_key_and_rejects_automatic_payload_capture():
    with pytest.raises(ValidationError):
        Settings(studyforge_tracing=True)
    with pytest.raises(ValidationError):
        Settings(studyforge_trace_content=True)
    for flag in ("langsmith_tracing", "langchain_tracing_v2", "log_payloads"):
        with pytest.raises(ValidationError):
            Settings(**{flag: True})


@pytest.mark.unit
async def test_demo_exercises_actual_graph_consent_research_and_failure():
    from evals.trace_demo import run_demo

    runs = await run_demo(offline=True)
    roots = [run for run in runs if run["parent_run_id"] is None]
    assert len(roots) == 5
    assert any(run.get("error") == "EXTERNAL_UNAVAILABLE" for run in roots)
    assert any(run["outputs"].get("evidence_status") == "insufficient" for run in roots)
    assert any(
        run["name"] == "research.consent"
        and run["outputs"]["research_accepted"] is False
        for run in runs
    )
    assert any(
        run["name"] == "retrieve" and run["outputs"].get("temporary_count") == 2
        for run in runs
    )
    assert "A célula é" not in json.dumps(runs, default=str)


@pytest.mark.contract
def test_status_requires_session_and_disclosure_mentions_external_tracing():
    from app.main import create_app
    from fastapi.testclient import TestClient
    from tests.support import headers

    app = create_app(configured())
    sink = Sink()
    app.state.observability.client = sink
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        assert client.get("/api/observability").status_code == 410
        headers(client)
        response = client.get("/api/observability")
        assert response.json()["enabled"] is True
        assert "synthetic-key" not in response.text
        assert (
            "LangSmith" in client.get("/api/runtime").json()["provider"]["disclosure"]
        )


@pytest.mark.contract
def test_detailed_mode_is_disclosed_in_runtime_and_status():
    from app.main import create_app
    from fastapi.testclient import TestClient
    from tests.support import headers

    app = create_app(
        Settings(
            studyforge_tracing=True,
            studyforge_trace_content=True,
            langsmith_api_key="synthetic-key",
        )
    )
    app.state.observability.client = Sink()
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        headers(client)
        assert client.get("/api/observability").json()["capture"] == "content"
        disclosure = client.get("/api/runtime").json()["provider"]["disclosure"]
        assert "prompts e respostas" in disclosure
        assert "armazenados no LangSmith" in disclosure
