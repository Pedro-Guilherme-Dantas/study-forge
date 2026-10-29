from uuid import UUID
from fastapi import APIRouter, Request, Response
from app.schemas import (
    OfferRequest,
    OfferDecision,
    ResearchRequest,
    ResearchReceipt,
    ResearchResult,
    TurnRequest,
)
from app.errors import AppError

router = APIRouter()


@router.post(
    "/api/conversations/{conversation_id}/research",
    response_model=ResearchReceipt,
    status_code=202,
    operation_id="createResearch",
)
async def create_research(
    request: Request, conversation_id: UUID, body: ResearchRequest
):
    conversation = request.app.state.store.get_conversation(
        request.state.session, conversation_id
    )
    turn_id = await request.app.state.orchestrator.start(
        conversation, TurnRequest(message=body.topic, intent="research")
    )
    return ResearchReceipt(research_id=conversation.turns[turn_id].research_id)


@router.post(
    "/api/conversations/{conversation_id}/research-offers/{offer_id}/decision",
    response_model=OfferDecision,
    operation_id="decideResearchOffer",
)
async def decide_offer(
    request: Request,
    response: Response,
    conversation_id: UUID,
    offer_id: UUID,
    body: OfferRequest,
):
    conversation = request.app.state.store.get_conversation(
        request.state.session, conversation_id
    )
    result = await request.app.state.orchestrator.decide(
        conversation, offer_id, body.accept
    )
    response.status_code = 202 if result.state == "accepted" else 200
    return result


@router.get(
    "/api/conversations/{conversation_id}/research/{research_id}",
    response_model=ResearchResult,
    operation_id="getResearch",
)
async def get_research(request: Request, conversation_id: UUID, research_id: UUID):
    conversation = request.app.state.store.get_conversation(
        request.state.session, conversation_id
    )
    value = conversation.research.get(str(research_id))
    if not value:
        raise AppError("NOT_FOUND", "Pesquisa não encontrada.", 404)
    return value
