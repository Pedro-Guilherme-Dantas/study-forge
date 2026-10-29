from uuid import UUID
from fastapi import APIRouter, Request
from app.schemas import IngestionReceipt

router = APIRouter()


@router.get(
    "/api/operations/{operation_id}",
    response_model=IngestionReceipt,
    operation_id="getOperation",
)
async def get_operation(request: Request, operation_id: UUID):
    return await request.app.state.ingestion.get_operation(operation_id)


@router.post(
    "/api/operations/{operation_id}/retry",
    response_model=IngestionReceipt,
    status_code=202,
    operation_id="retryIngestion",
)
async def retry_ingestion(request: Request, operation_id: UUID):
    return await request.app.state.ingestion.retry(operation_id)
