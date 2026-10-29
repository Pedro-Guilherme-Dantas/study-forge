from fastapi import APIRouter, Request
from sqlalchemy import select
from app.db.models import IngestionOperation
from app.ingestion.service import receipt
from app.schemas import ProgressSnapshot, ResearchSummary

router = APIRouter()


@router.get(
    "/api/progress", response_model=ProgressSnapshot, operation_id="getProgress"
)
async def get_progress(request: Request):
    materials = (await request.app.state.ingestion.list_materials()).items
    async with request.app.state.database() as db:
        operations = (
            await db.scalars(
                select(IngestionOperation)
                .order_by(IngestionOperation.created_at.desc())
                .limit(100)
            )
        ).all()
        ingestions = [receipt(operation) for operation in operations]
    conversation = request.state.session.conversation
    research = (
        []
        if not conversation
        else [
            ResearchSummary(research_id=r.research_id, status=r.status)
            for r in conversation.research.values()
        ]
    )
    return ProgressSnapshot(
        materials=materials, ingestions=ingestions, research=research
    )
