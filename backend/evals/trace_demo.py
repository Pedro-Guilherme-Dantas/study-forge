"""Deterministic observability rehearsal; no DB, Gemini or search calls.

Run with --offline for a local structural check, or configure the LangSmith key
to export the same scenarios. Fixtures demonstrate control flow, not LLM quality.
"""

import argparse
import asyncio
import json
from uuid import uuid4

from app.agents.graph import build_tutor_graph
from app.agents.orchestrator import Orchestrator
from app.agents.tutor import Tutor
from app.agents.researcher import Researcher
from app.providers.search import SearchProvider
from app.diagnostics import configure
from app.errors import AppError
from app.observability import Observability
from app.operations import Executor
from app.providers.gemini import GeminiProvider
from app.retrieval import Evidence
from app.schemas import LibraryChunk, Locator, TurnRequest
from app.sessions import Conversation
from app.settings import Settings


class FixtureRetriever:
    def __init__(self, scenario):
        self.scenario = scenario

    async def retrieve(self, question, budget, temporary=()):
        if self.scenario == "failure":
            raise AppError(
                "EXTERNAL_UNAVAILABLE", "Falha simulada de recuperação.", 502
            )
        if self.scenario == "insufficient":
            return []
        if self.scenario == "research":
            return [Evidence(snapshot.passages[0], 0.1) for snapshot in temporary]
        text = "A célula é a unidade básica dos seres vivos."
        return [
            Evidence(
                LibraryChunk(
                    material_id=uuid4(),
                    version_id=uuid4(),
                    chunk_id="demo-cell",
                    text=text,
                    display_name="Fixture de demonstração",
                    source_kind="markdown_upload",
                    locator=Locator(
                        kind="markdown_original",
                        section_path=["Célula"],
                        start_char=0,
                        end_char=len(text),
                        start_line=1,
                        end_line=1,
                    ),
                ),
                0.1,
            )
        ]


class OfflineSink:
    def __init__(self):
        self.runs = []

    async def create_run(self, **run):
        self.runs.append(run)

    async def aclose(self):
        pass


async def run_demo(offline=False, content=None):
    configure()
    settings = Settings(
        app_mode="fixture",
        studyforge_tracing=True,
        **({"studyforge_trace_content": content} if content is not None else {}),
        **({"langsmith_api_key": "offline-fixture"} if offline else {}),
    )
    sink = OfflineSink() if offline else None
    tracing = Observability(settings, client=sink)
    executor = Executor()
    await tracing.start()
    results = []
    try:
        for scenario in ("retrieved", "insufficient", "failure", "research"):
            orchestrator = Orchestrator(
                settings,
                build_tutor_graph(
                    FixtureRetriever(scenario),
                    Tutor(settings, GeminiProvider(settings)),
                ),
                executor,
                researcher=Researcher(
                    settings, SearchProvider(settings), None, GeminiProvider(settings)
                ),
                observability=tracing,
            )
            conversation = Conversation()
            turn_id = await orchestrator.start(
                conversation,
                TurnRequest(
                    message="Explique célula",
                    intent="research" if scenario == "research" else "auto",
                ),
            )
            await asyncio.gather(*list(conversation.tasks))
            result = conversation.turns[turn_id]
            results.append(
                {"scenario": scenario, "turn_id": turn_id, "status": result.status}
            )
            if scenario == "insufficient":
                await orchestrator.decide(
                    conversation, result.research_offer.offer_id, False
                )
        await asyncio.wait_for(tracing.flush(), 45)
        status = tracing.status()
        print(
            json.dumps(
                {
                    "mode": "offline" if offline else "langsmith",
                    "scenarios": results,
                    "export": status,
                },
                indent=2,
            )
        )
        if status["failed"] or status["dropped"] or status["sent"] != 5:
            raise SystemExit(
                "Exportação incompleta; verifique chave, região, destino e cota."
            )
    finally:
        await executor.shutdown()
        await tracing.close()
    return sink.runs if sink else None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    asyncio.run(run_demo(parser.parse_args().offline))
