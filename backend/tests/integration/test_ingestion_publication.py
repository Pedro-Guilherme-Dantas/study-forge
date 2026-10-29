import asyncio
import pytest
from sqlalchemy import select, func
from app.db.models import Chunk, Material, MaterialVersion, IngestionOperation
from app.providers.gemini import GeminiProvider
from app.settings import Settings
from app.errors import AppError
from tests.support import service_for


@pytest.mark.integration
async def test_last_vector_invalid_never_publishes_partial(library_url):
    class InvalidProvider:
        async def embed(self, values):
            vectors = [[1.0] + [0.0] * 767 for _ in values]
            vectors[-1] = [float("nan")] * 768
            return vectors

    engine, database, executor, service = service_for(library_url, InvalidProvider())
    receipt = await service.accept_markdown(
        "test.md", ("# Title\n\n" + "Useful content. " * 60).encode()
    )
    await executor.drain()
    async with database() as session:
        operation = await session.get(IngestionOperation, receipt.operation_id)
        assert operation.state == "failed"
        assert await session.scalar(select(func.count()).select_from(Chunk)) == 0
        assert (
            await session.get(Material, receipt.material_id)
        ).active_version_id is None
    await engine.dispose()


@pytest.mark.integration
async def test_scheduling_failure_is_retryable_and_releases_admission(
    library_url, monkeypatch
):
    engine, database, executor, service = service_for(library_url)
    original = executor.submit

    def fail(*args):
        raise RuntimeError("synthetic scheduling failure")

    monkeypatch.setattr(executor, "submit", fail)
    with pytest.raises(AppError) as failure:
        await service.accept_markdown("schedule.md", b"# Scheduling\n\nText")
    assert failure.value.code == "EXECUTION_INTERRUPTED" and executor.pending == 0
    async with database() as session:
        operation = await session.scalar(select(IngestionOperation))
        assert operation.state == "interrupted"
        operation_id = operation.id
        assert await session.scalar(select(func.count()).select_from(Chunk)) == 0
    monkeypatch.setattr(executor, "submit", original)
    await service.retry(operation_id)
    await executor.drain()
    assert (await service.get_operation(operation_id)).state == "succeeded"
    await engine.dispose()


@pytest.mark.integration
async def test_repeated_concurrent_upload_and_old_retry_cannot_regress(library_url):
    class FailsOnce:
        def __init__(self):
            self.failed = False
            self.fixture = GeminiProvider(Settings())

        async def embed(self, values):
            if not self.failed:
                self.failed = True
                raise RuntimeError("synthetic provider failure")
            return await self.fixture.embed(values)

    engine, database, executor, service = service_for(library_url, FailsOnce())
    first, duplicate = await asyncio.gather(
        service.accept_markdown("a.md", b"# First\n\ntext"),
        service.accept_markdown("a.md", b"# First\n\ntext"),
    )
    assert first.operation_id == duplicate.operation_id
    await executor.drain()
    assert (await service.get_operation(first.operation_id)).state == "failed"
    second = await service.accept_markdown("a.md", b"# Second\n\nnewer text")
    await executor.drain()
    await service.retry(first.operation_id)
    await executor.drain()
    async with database() as session:
        material = await session.get(Material, first.material_id)
        assert material.active_version_id == second.version_id
        assert (await session.get(MaterialVersion, first.version_id)).state == "ready"
    await engine.dispose()


@pytest.mark.integration
async def test_orphaned_queued_and_running_operations_are_interrupted(library_url):
    engine, database, executor, service = service_for(library_url)
    receipt = await service.accept_markdown("recover.md", b"# Recovery\n\ntext")
    await executor.drain()
    for state in ("queued", "running"):
        async with database() as session, session.begin():
            operation = await session.get(IngestionOperation, receipt.operation_id)
            operation.state, operation.runner_instance_id = state, None
            version = await session.get(MaterialVersion, receipt.version_id)
            version.state = "processing"
        await service.recover()
        async with database() as session:
            assert (
                await session.get(IngestionOperation, receipt.operation_id)
            ).state == "interrupted"
    await engine.dispose()
