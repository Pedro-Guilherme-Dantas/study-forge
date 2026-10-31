"""Ephemeral graph; explicit opt-in spans never serialize its runtime state."""

from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from app.observability import observed, annotate, capture_content, evidence_documents


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

    @observed("orchestrator")
    async def orchestrate(state):
        state["budget"].step()
        annotate(research_authorized=bool(state.get("authorized_research")))
        capture_content(
            inputs={"question": state["question"]},
            outputs={
                "next_step": "researcher"
                if state.get("authorized_research")
                else "retrieve",
            },
        )
        return {
            "delegation": ["orchestrator"]
            + (["researcher"] if state.get("authorized_research") else [])
            + ["retrieve", "tutor"]
        }

    @observed("researcher")
    async def research(state):
        state["budget"].step()
        capture_content(inputs={"question": state["question"]})
        # Only application code supplies this capability after explicit user intent/consent.
        # Neither retrieved content nor a model output can set it.
        if not state.get("authorized_research"):
            raise RuntimeError("Research requires application authorization")
        return await state["research_callback"]()

    @observed("retrieve", "retriever")
    async def retrieve(state):
        state["budget"].step()
        capture_content(inputs={"query": state["question"]})
        results = await retriever.retrieve(
            state["question"], state["budget"], state.get("temporary", ())
        )
        annotate(
            count=len(results),
            temporary_count=sum(hasattr(item.passage, "source_id") for item in results),
            library_count=sum(
                not hasattr(item.passage, "source_id") for item in results
            ),
        )
        capture_content(outputs={"documents": evidence_documents(results)})
        return {"evidence": EvidenceSet.from_results(results)}

    @observed("tutor")
    async def teach(state):
        capture_content(
            inputs={
                "question": state["question"],
                "documents": evidence_documents(state["evidence"].items.values()),
            }
        )
        output = await tutor.teach(
            state["question"], state["evidence"], state["budget"]
        )
        annotate(
            evidence_status=output.evidence_status,
            citation_count=len(output.citation_ids),
        )
        capture_content(outputs=output.model_dump(mode="json"))
        return {"output": output}

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
