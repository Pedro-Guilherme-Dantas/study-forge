from uuid import UUID
from fastapi import APIRouter, Request
from app.errors import AppError
from app.schemas import LibraryCitation, TemporaryCitation

router = APIRouter()


@router.get(
    "/api/conversations/{conversation_id}/citations/{citation_id}",
    response_model=LibraryCitation | TemporaryCitation,
    operation_id="getCitation",
)
async def get_citation(request: Request, conversation_id: UUID, citation_id: str):
    conversation = request.app.state.store.get_conversation(
        request.state.session, conversation_id
    )
    citation = conversation.citations.get(citation_id)
    if not citation:
        raise AppError("NOT_FOUND", "Referência não encontrada nesta conversa.", 404)
    return citation
