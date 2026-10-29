import asyncio
import pytest
from sqlalchemy import text, select, func
from app.ingestion.promotion import PromotionService
from app.db.models import SelectionGrant
from tests.support import prepare_research_session as prepare


@pytest.mark.integration
async def test_sql_lock_barrier_linearizes_selection_before_close(library_url):
    (
        engine,
        database,
        executor,
        ingestion,
        store,
        session,
        conversation,
        snapshots,
    ) = await prepare(library_url)
    source = snapshots[0].summary
    async with database() as barrier:
        await barrier.execute(text("SELECT pg_advisory_xact_lock(72198341)"))
        selection = asyncio.create_task(
            PromotionService(ingestion).select(
                conversation, source.source_id, source.snapshot_hash
            )
        )
        for _ in range(200):
            if conversation.lock.locked():
                break
            await asyncio.sleep(0.005)
        assert conversation.lock.locked()
        closing = asyncio.create_task(store.close(session, conversation.id))
        await asyncio.sleep(0)
        assert not closing.done() and not selection.done()
        await barrier.commit()
        receipt = await selection
        await closing
    await executor.drain()
    assert (await ingestion.get_operation(receipt.operation_id)).state == "succeeded"
    async with database() as db:
        assert await db.scalar(select(func.count()).select_from(SelectionGrant)) == 1
    assert conversation.closed and not conversation.sources
    await engine.dispose()
