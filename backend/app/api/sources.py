from uuid import UUID
from fastapi import APIRouter, Request, Response, Header
from typing import Annotated
from app.errors import AppError
from app.schemas import TemporarySourceDetail, SelectionRequest, PromotionReceipt

router = APIRouter()


@router.post(
    "/api/conversations/{conversation_id}/sources/{source_id}/selection",
    response_model=PromotionReceipt,
    operation_id="selectSource",
)
async def select_source(
    request: Request,
    response: Response,
    conversation_id: UUID,
    source_id: UUID,
    body: SelectionRequest,
    idempotency_key: Annotated[
        str | None, Header(alias="Idempotency-Key", min_length=8, max_length=128)
    ] = None,
):
    conversation = request.app.state.store.get_conversation(
        request.state.session, conversation_id
    )
    receipt = await request.app.state.promotion.select(
        conversation,
        source_id,
        body.snapshot_hash,
        idempotency_key,
    )
    response.status_code = 202 if receipt.selection_status == "accepted" else 200
    return receipt


@router.get(
    "/api/conversations/{conversation_id}/sources/{source_id}",
    response_model=TemporarySourceDetail,
    operation_id="getTemporarySource",
)
async def get_source(request: Request, conversation_id: UUID, source_id: UUID):
    conversation = request.app.state.store.get_conversation(
        request.state.session, conversation_id
    )
    snapshot = conversation.sources.get(str(source_id))
    if not snapshot:
        raise AppError(
            "SOURCE_EXPIRED", "A fonte temporária não está mais disponível.", 410
        )
    return TemporarySourceDetail(
        source=snapshot.summary,
        snapshot_text=snapshot.text,
        pipeline_fingerprint=snapshot.fingerprint,
    )
