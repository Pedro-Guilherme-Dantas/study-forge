"""Inspect actual SQL rows and writable runtime locations for an unselected marker."""

from dataclasses import replace
from pathlib import Path
from uuid import uuid4
import pytest
from sqlalchemy import text
from app.ingestion.chunk import digest
from app.ingestion.promotion import PromotionService
from app.operations import Budget
from app.agents.tutor import Tutor
from app.retrieval import Retriever
from app.citations import EvidenceSet
from tests.support import prepare_research_session as prepare


@pytest.mark.integration
async def test_unselected_content_and_derived_answer_absent_from_sql_logs_and_runtime_files(
    library_url, caplog
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
    marker = "UNSELECTED_" + uuid4().hex
    source = snapshots[1]
    url = "https://example.org/" + marker
    # A unique-token fixture avoids random hash collisions with unrelated passages.
    # This test checks retention, not the relevance of the fixture embedding.
    body = " ".join([marker] * 4)
    summary = source.summary.model_copy(
        update={
            "title": marker,
            "origin_url": url,
            "preview": body,
            "snapshot_hash": digest(body),
        }
    )
    vector = (await ingestion.provider.embed([body]))[0]
    passage = replace(
        source.passages[0],
        text=body,
        display_name=marker,
        origin_url=url,
        snapshot_hash=digest(body),
        embedding=vector,
    )
    source = replace(
        source, text=body, summary=summary, passages=[passage], effective_url=url
    )
    conversation.sources[str(summary.source_id)] = source
    retrieved = await Retriever(
        ingestion.settings, database, ingestion.provider
    ).retrieve(marker, Budget(5), list(conversation.sources.values()))
    evidence = EvidenceSet.from_results(retrieved)
    answer = await Tutor(ingestion.settings, ingestion.provider).teach(
        marker, evidence, Budget(5)
    )
    assert marker in answer.answer_markdown
    conversation.messages.append({"role": "assistant", "text": answer.answer_markdown})
    selected = snapshots[0].summary
    receipt = await PromotionService(ingestion).select(
        conversation, selected.source_id, selected.snapshot_hash
    )
    await executor.drain()
    assert (await ingestion.get_operation(receipt.operation_id)).state == "succeeded"
    async with database() as db:
        tables = (
            (
                await db.execute(
                    text(
                        "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"
                    )
                )
            )
            .scalars()
            .all()
        )
        for table in tables:
            rows = (
                (
                    await db.execute(
                        text(f'SELECT row_to_json(row)::text FROM "{table}" AS row')
                    )
                )
                .scalars()
                .all()
            )
            assert all(marker not in row for row in rows), table
    assert marker not in caplog.text
    for root in (Path("/tmp"), Path("/home/studyforge/.cache")):
        if not root.exists():
            continue
        for file in root.rglob("*"):
            if file.is_file() and file.stat().st_size < 10_000_000:
                assert marker.encode() not in file.read_bytes(), file.name
    await store.close(session, conversation.id)
    assert (
        not conversation.messages
        and not conversation.sources
        and not conversation.citations
    )
    await engine.dispose()
