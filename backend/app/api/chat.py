from uuid import UUID
from fastapi import APIRouter, Request, Response
from app.errors import AppError
from app.schemas import ConversationReceipt, TurnRequest, TurnReceipt, TurnResult

router = APIRouter()


@router.post(
    "/api/conversations",
    response_model=ConversationReceipt,
    status_code=201,
    operation_id="createConversation",
)
async def create_conversation(request: Request):
    conversation = request.app.state.store.create_conversation(request.state.session)
    return ConversationReceipt(
        conversation_id=conversation.id,
        server_instance_id=request.app.state.store.instance_id,
        epoch=conversation.epoch,
    )


@router.delete(
    "/api/conversations/{conversation_id}",
    status_code=204,
    operation_id="closeConversation",
)
async def close_conversation(request: Request, conversation_id: UUID):
    await request.app.state.store.close(request.state.session, conversation_id)
    return Response(status_code=204)


@router.post(
    "/api/conversations/{conversation_id}/turns",
    response_model=TurnReceipt,
    status_code=202,
    operation_id="createTurn",
)
async def create_turn(request: Request, conversation_id: UUID, body: TurnRequest):
    conversation = request.app.state.store.get_conversation(
        request.state.session, conversation_id
    )
    turn_id = await request.app.state.orchestrator.start(conversation, body)
    return TurnReceipt(turn_id=turn_id)


@router.get(
    "/api/conversations/{conversation_id}/turns/{turn_id}",
    response_model=TurnResult,
    operation_id="getTurn",
)
async def get_turn(request: Request, conversation_id: UUID, turn_id: UUID):
    conversation = request.app.state.store.get_conversation(
        request.state.session, conversation_id
    )
    result = conversation.turns.get(str(turn_id))
    if not result:
        raise AppError("NOT_FOUND", "Resposta não encontrada nesta conversa.", 404)
    return result
