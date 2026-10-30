"""Exact cosine retrieval, restricted to published versions and one embedding profile."""

from dataclasses import dataclass
from sqlalchemy import select
from app.db.models import Chunk, Material, MaterialVersion
from app.providers.gemini import GeminiProvider
from app.schemas import LibraryChunk, Locator


@dataclass(frozen=True)
class Evidence:
    passage: LibraryChunk
    distance: float


class Retriever:
    def __init__(self, settings, database, provider):
        self.settings, self.database, self.provider = settings, database, provider

    async def retrieve(self, question, budget, temporary=()):
        temporary = [
            snapshot
            for snapshot in temporary
            if snapshot.embedding_profile == self.settings.embedding_profile
            and snapshot.passages
        ]
        available = (
            select(Chunk, Material)
            .join(MaterialVersion, Chunk.material_version_id == MaterialVersion.id)
            .join(Material, Material.active_version_id == MaterialVersion.id)
            .where(
                MaterialVersion.state == "ready",
                MaterialVersion.material_id == Material.id,
                Chunk.embedding_profile_id == self.settings.embedding_profile,
                MaterialVersion.embedding_profile_id == self.settings.embedding_profile,
            )
        )
        if not temporary:
            async with self.database() as session:
                if (
                    await session.scalar(available.with_only_columns(Chunk.id).limit(1))
                    is None
                ):
                    return []
        vectors = await self.provider.embed([question], query=True, budget=budget)
        vector = GeminiProvider.validate_vector(vectors[0])
        distance = Chunk.embedding.cosine_distance(vector)
        query = (
            available.add_columns(distance.label("distance"))
            .order_by(distance, Chunk.id)
            .limit(self.settings.retrieval_top_k)
        )
        async with self.database() as session:
            rows = (await session.execute(query)).all()
        results = [
            Evidence(
                LibraryChunk(
                    material_id=m.id,
                    version_id=c.material_version_id,
                    chunk_id=c.id,
                    text=c.text,
                    locator=Locator.model_validate(c.locator),
                    source_kind=m.source_kind,
                    display_name=m.display_name,
                    origin_url=m.effective_url,
                ),
                float(d),
            )
            for c, m, d in rows
        ]
        for snapshot in temporary:
            if snapshot.embedding_profile != self.settings.embedding_profile:
                continue
            for passage in snapshot.passages:
                distance = 1 - sum(a * b for a, b in zip(vector, passage.embedding))
                results.append(Evidence(passage, distance))
        return sorted(
            results,
            key=lambda item: (
                item.distance,
                getattr(item.passage, "chunk_id", None)
                or str(item.passage.source_id)
                + ":"
                + str(item.passage.locator.start_char),
            ),
        )[: self.settings.retrieval_top_k]
