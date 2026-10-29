from uuid import uuid4
import pytest
from app.agents.orchestrator import Orchestrator
from app.operations import Budget
from app.settings import Settings
from app.sessions import Conversation
from app.errors import AppError


@pytest.mark.parametrize("fails", [False, True])
async def test_collection_deadline_is_reserved_and_turn_deadline_restored(fails):
    budget = Budget(60)
    original = budget.deadline

    class Collector:
        async def collect(self, topic, shared):
            assert shared is budget and shared.deadline < original
            if fails:
                raise AppError("SOURCE_UNAVAILABLE", "Synthetic", 502)
            return [], [], []

    orchestrator = Orchestrator(Settings(), None, None, Collector())
    conversation = Conversation()
    research_id = str(uuid4())
    if fails:
        with pytest.raises(AppError):
            await orchestrator.research(
                conversation, 0, "synthetic", budget, research_id
            )
    else:
        await orchestrator.research(conversation, 0, "synthetic", budget, research_id)
    assert budget.deadline == original
