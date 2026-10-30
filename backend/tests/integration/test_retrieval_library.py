import pytest
from sqlalchemy import select
from app.db.models import Chunk, Material
from app.operations import Budget
from app.retrieval import Retriever
from tests.support import service_for


@pytest.mark.integration
async def test_empty_library_never_requests_an_external_query_vector(library_url):
    engine, database, executor, service = service_for(library_url)

    class ForbiddenProvider:
        async def embed(self, *args, **kwargs):
            pytest.fail("An empty knowledge base must not consume embedding quota")

    try:
        assert (
            await Retriever(service.settings, database, ForbiddenProvider()).retrieve(
                "Authored question", Budget(2)
            )
            == []
        )
    finally:
        await engine.dispose()


@pytest.mark.integration
async def test_exact_ranking_only_active_ready_profile(library_url):
    engine, database, executor, service = service_for(library_url)
    first = await service.accept_markdown("same.md", b"# Old\n\nold content")
    await executor.drain()
    second = await service.accept_markdown("same.md", b"# New\n\nnew content")
    await executor.drain()
    other = await service.accept_markdown("other.md", b"# Other\n\nother content")
    await executor.drain()
    await service.accept_markdown("third.md", b"# Third\n\nthird content")
    await executor.drain()
    async with database() as session, session.begin():
        for chunk in (await session.scalars(select(Chunk))).all():
            chunk.embedding = (
                [1.0, 0.0] + [0.0] * 766
                if chunk.material_version_id == second.version_id
                else [0.0, 1.0] + [0.0] * 766
            )

    class QueryProvider:
        async def embed(self, *args, **kwargs):
            return [[1.0] + [0.0] * 767]

    retriever = Retriever(service.settings, database, QueryProvider())
    results = await retriever.retrieve("query", Budget(2))
    assert results[0].passage.version_id == second.version_id
    assert results[0].distance == pytest.approx(0)
    assert first.version_id not in [item.passage.version_id for item in results]
    assert len(results) == 3
    assert [item.passage.chunk_id for item in results[1:]] == sorted(
        item.passage.chunk_id for item in results[1:]
    )
    service.settings.app_mode = "real"
    assert await retriever.retrieve("query", Budget(2)) == []
    await engine.dispose()
