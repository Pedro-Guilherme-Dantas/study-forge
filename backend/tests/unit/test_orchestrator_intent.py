import pytest
from app.agents.orchestrator import Orchestrator, ResearchIntent
from app.operations import Budget
from app.settings import Settings


@pytest.mark.parametrize("intent,quote,expected", [
    ("research", "Consulte fontes na internet", True),
    ("retrieval", "", False),
    ("ambiguous", "", False),
    ("research", "pedido que não existe", False),
    ("research", "", False),
])
async def test_structured_intent_requires_quote_from_current_message(intent, quote, expected):
    class Provider:
        async def generate(self, prompt, schema, **kwargs):
            assert schema is ResearchIntent
            assert '"message"' in prompt
            return schema(intent=intent, request_quote=quote)

    orchestrator = Orchestrator(Settings(app_mode="real"), None, None, provider=Provider())
    assert await orchestrator.classify_research("Consulte fontes na internet sobre células", Budget(20)) is expected


@pytest.mark.parametrize("message,expected", [
    ("Pesquise na internet sobre células", True),
    ("Não pesquise na internet", False),
    ("Explique células", False),
])
async def test_failed_model_uses_existing_explicit_intent_fallback(message, expected):
    class Provider:
        async def generate(self, *args, **kwargs):
            raise RuntimeError("unavailable")

    orchestrator = Orchestrator(Settings(app_mode="real"), None, None, provider=Provider())
    assert await orchestrator.classify_research(message, Budget(20)) is expected


async def test_evaluation_does_not_count_fallback_as_model_success():
    class Provider:
        async def generate(self, *args, **kwargs):
            raise RuntimeError("model unavailable")

    orchestrator = Orchestrator(Settings(app_mode="real"), None, None, provider=Provider())
    with pytest.raises(RuntimeError, match="model unavailable"):
        await orchestrator.classify_research(
            "Pesquise na internet sobre células", Budget(20), allow_fallback=False
        )


@pytest.mark.parametrize("intent,expected", [("research", True), ("retrieval", False), ("ambiguous", False)])
async def test_model_decision_routes_actual_graph_and_registers_research(intent, expected):
    from app.agents.graph import build_tutor_graph
    from app.agents.tutor import TutorOutput
    from app.schemas import TurnRequest, TurnResult
    from app.sessions import Conversation
    from uuid import uuid4

    message = "Consulte fontes na internet sobre células"

    class Provider:
        async def generate(self, prompt, schema, **kwargs):
            return schema(intent=intent, request_quote=message if expected else "")

    class Retriever:
        async def retrieve(self, *args):
            return []

    class Tutor:
        async def teach(self, *args):
            return TutorOutput(answer_markdown="Sem evidências.", evidence_status="insufficient")

    class Researcher:
        calls = 0
        async def collect(self, *args):
            self.calls += 1
            return [], [], []

    researcher = Researcher()
    orchestrator = Orchestrator(
        Settings(app_mode="real"), build_tutor_graph(Retriever(), Tutor()), None,
        researcher, provider=Provider(),
    )
    conversation = Conversation()
    turn = str(uuid4())
    conversation.turns[turn] = TurnResult(turn_id=turn, status="running")
    await orchestrator.run(conversation, 0, turn, TurnRequest(message=message))
    assert researcher.calls == int(expected)
    result = conversation.turns[turn]
    if expected:
        assert conversation.research[str(result.research_id)].status == "empty"
        assert result.research_offer is None
    else:
        assert not conversation.research
        assert result.research_offer is not None
