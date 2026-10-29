import asyncio
from dataclasses import replace
import pytest
from sqlalchemy import select, func
from app.ingestion.promotion import PromotionService
from app.ingestion.chunk import digest
from app.db.models import Material, MaterialVersion, Chunk, SelectionGrant
from app.db.models import IngestionOperation
from app.errors import AppError
from tests.support import prepare_research_session as prepare


@pytest.mark.integration
async def test_concurrent_selection_single_grant_and_close_after_commit(library_url):
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
    selected = snapshots[0]
    promotion = PromotionService(ingestion)
    first, second = await asyncio.gather(
        *(
            promotion.select(
                conversation, selected.summary.source_id, selected.summary.snapshot_hash
            )
            for _ in range(2)
        )
    )
    assert first.operation_id == second.operation_id
    await store.close(session, conversation.id)
    await executor.drain()
    assert (await ingestion.get_operation(first.operation_id)).state == "succeeded"
    assert (
        conversation.sources == {}
        and conversation.messages == []
        and conversation.closed
    )
    async with database() as db:
        assert await db.scalar(select(func.count()).select_from(SelectionGrant)) == 1
        assert await db.scalar(select(func.count()).select_from(Material)) == 1
        assert (
            await db.scalar(select(Material))
        ).original_url == selected.summary.origin_url
    await engine.dispose()


@pytest.mark.integration
async def test_duplicate_selection_returns_receipt_even_when_executor_is_full(
    library_url,
):
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
    promotion = PromotionService(ingestion)
    first = await promotion.select(conversation, source.source_id, source.snapshot_hash)
    await executor.drain()
    tickets = [executor.reserve() for _ in range(executor.capacity)]
    try:
        repeated = await promotion.select(
            conversation, source.source_id, source.snapshot_hash
        )
        assert repeated.operation_id == first.operation_id
        assert repeated.selection_status == "already_accepted"
        other = snapshots[1].summary
        with pytest.raises(AppError) as failure:
            await promotion.select(conversation, other.source_id, other.snapshot_hash)
        assert failure.value.code == "EXECUTION_LIMIT"
        async with database() as db:
            assert (
                await db.scalar(select(func.count()).select_from(SelectionGrant)) == 1
            )
            assert await db.scalar(select(func.count()).select_from(Material)) == 1
        assert executor.pending == executor.capacity
    finally:
        for ticket in tickets:
            ticket.release()
        await store.close(session, conversation.id)
        await engine.dispose()


@pytest.mark.integration
async def test_selection_commit_then_scheduling_failure_recovers_without_conversation(
    library_url, monkeypatch
):
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
    original = executor.submit

    def fail(*args):
        raise RuntimeError("synthetic schedule failure")

    monkeypatch.setattr(executor, "submit", fail)
    source = snapshots[0].summary
    with pytest.raises(AppError):
        await PromotionService(ingestion).select(
            conversation, source.source_id, source.snapshot_hash
        )
    assert executor.pending == 0
    async with database() as db:
        operation = await db.scalar(select(IngestionOperation))
        assert operation.state == "interrupted"
        assert await db.scalar(select(func.count()).select_from(SelectionGrant)) == 1
        operation_id = operation.id
    await store.close(session, conversation.id)
    monkeypatch.setattr(executor, "submit", original)
    await ingestion.retry(operation_id)
    await executor.drain()
    assert (await ingestion.get_operation(operation_id)).state == "succeeded"
    await engine.dispose()


@pytest.mark.integration
async def test_close_before_selection_never_writes(library_url):
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
    await store.close(session, conversation.id)
    with pytest.raises(AppError) as failure:
        await PromotionService(ingestion).select(
            conversation, source.source_id, source.snapshot_hash
        )
    assert failure.value.status == 410
    async with database() as db:
        assert await db.scalar(select(func.count()).select_from(Material)) == 0
        assert await db.scalar(select(func.count()).select_from(SelectionGrant)) == 0
    await engine.dispose()


@pytest.mark.integration
async def test_selected_only_retention_and_failed_embedding_no_chunks(
    library_url, capsys
):
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
    unselected = snapshots[1]
    marker = "UNSELECTED_PRIVATE_MARKER_B_7843"
    unselected = replace(
        unselected,
        text=marker,
        summary=unselected.summary.model_copy(
            update={"title": marker, "preview": marker, "snapshot_hash": digest(marker)}
        ),
    )
    conversation.sources[str(unselected.summary.source_id)] = unselected

    class FailingProvider:
        async def embed(self, *args, **kwargs):
            raise RuntimeError(marker)

    ingestion.provider = FailingProvider()
    selected = snapshots[0].summary
    receipt = await PromotionService(ingestion).select(
        conversation, selected.source_id, selected.snapshot_hash
    )
    await executor.drain()
    assert (await ingestion.get_operation(receipt.operation_id)).state == "failed"
    async with database() as db:
        texts = (await db.scalars(select(MaterialVersion.input_snapshot_text))).all()
        assert len(texts) == 1 and marker not in texts[0]
        assert await db.scalar(select(func.count()).select_from(Chunk)) == 0
    await store.close(session, conversation.id)
    assert marker not in capsys.readouterr().out
    await engine.dispose()
