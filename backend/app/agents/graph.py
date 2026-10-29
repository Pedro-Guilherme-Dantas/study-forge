"""Ephemeral graph: no checkpoint, remote trace, tool capable of persistence or store."""

from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END


class TutorState(TypedDict, total=False):
    question: str
    budget: Any
    evidence: Any
    output: Any
    delegation: list[str]
    temporary: list
    authorized_research: bool
    research_callback: Any
    research_id: str | None


def build_tutor_graph(retriever, tutor):
    from app.citations import EvidenceSet

    async def orchestrate(state):
        state["budget"].step()
        return {
            "delegation": ["orchestrator"]
            + (["researcher"] if state.get("authorized_research") else [])
            + ["retrieve", "tutor"]
        }

    async def research(state):
        state["budget"].step()
        # Only application code supplies this capability after explicit user intent/consent.
        # Neither retrieved content nor a model output can set it.
        if not state.get("authorized_research"):
            raise RuntimeError("Research requires application authorization")
        return await state["research_callback"]()

    async def retrieve(state):
        state["budget"].step()
        results = await retriever.retrieve(
            state["question"], state["budget"], state.get("temporary", ())
        )
        return {"evidence": EvidenceSet.from_results(results)}

    async def teach(state):
        return {
            "output": await tutor.teach(
                state["question"], state["evidence"], state["budget"]
            )
        }

    graph = StateGraph(TutorState)
    graph.add_node("orchestrator", orchestrate)
    graph.add_node("retrieve", retrieve)
    graph.add_node("tutor", teach)
    graph.add_node("researcher", research)
    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator",
        lambda state: "researcher" if state.get("authorized_research") else "retrieve",
    )
    graph.add_edge("researcher", "retrieve")
    graph.add_edge("retrieve", "tutor")
    graph.add_edge("tutor", END)
    return graph.compile()
