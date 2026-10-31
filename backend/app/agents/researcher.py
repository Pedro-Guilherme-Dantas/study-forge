import asyncio
import hashlib
from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime, timezone
from app.errors import AppError
from app.schemas import SourceSummary, ResearchResult, Locator
from app.ingestion.extract_html import extract_html
from app.ingestion.normalize import normalize
from app.ingestion.chunk import chunk_text, digest, pipeline_fingerprint
from app.web_fetch import HtmlPage
from app.observability import annotate, observed, capture_content


@dataclass(frozen=True)
class TemporaryPassage:
    source_id: str
    snapshot_hash: str
    origin_url: str
    display_name: str
    text: str
    locator: Locator
    embedding: list


@dataclass(frozen=True)
class Snapshot:
    summary: SourceSummary
    text: str
    raw_hash: str
    fingerprint: str
    extraction_fingerprint: str
    effective_url: str
    passages: list[TemporaryPassage]
    embedding_profile: str


class Researcher:
    """Receives a server-authorized job, never a database writer or selection tool."""

    def __init__(self, settings, search, fetcher, provider):
        self.settings, self.search, self.fetcher, self.provider = (
            settings,
            search,
            fetcher,
            provider,
        )

    @observed("research.collect", "tool")
    async def collect(self, topic, budget):
        capture_content(inputs={"query": topic})
        budget.step()
        candidates = await self.search.discover(topic, budget)
        snapshots, errors, unavailable, visited = [], [], [], set()
        for candidate in candidates[: self.settings.max_pages_per_research]:
            if candidate["url"] in visited:
                continue
            visited.add(candidate["url"])
            source_id = str(uuid4())
            try:
                budget.check()
                if self.settings.app_mode == "fixture":
                    # Authored local HTML, never represented as an actual fetched page.
                    paragraph = (
                        "A célula é a unidade básica da vida. A membrana delimita o ambiente celular. "
                        "O estudo da organização celular relaciona estrutura, energia e funcionamento dos seres vivos. "
                    )
                    body = (
                        "<html><head><title>Fixture local</title></head><body><article><h1>Estudo de células</h1><p>"
                        + paragraph * 6
                        + "</p></article></body></html>"
                    ).encode()
                    page = HtmlPage(candidate["url"], candidate["url"], body)
                else:
                    page = await self.fetcher.fetch(candidate["url"], budget)
                text, extraction = await asyncio.to_thread(extract_html, page.body)
                if len(text.encode()) > self.settings.max_temporary_bytes:
                    raise AppError(
                        "EXECUTION_LIMIT",
                        "A fonte excede a capacidade temporária.",
                        429,
                    )
                doc = await asyncio.to_thread(normalize, text)
                chunks = await asyncio.to_thread(chunk_text, doc, self.settings)
                vectors = await self.provider.embed(
                    [
                        " / ".join(chunk.locator.section_path) + "\n" + chunk.text
                        for chunk in chunks
                    ],
                    budget=budget,
                )
                if len(vectors) != len(chunks):
                    raise AppError(
                        "INVALID_EMBEDDING",
                        "Vetores temporários incompletos.",
                        502,
                        "embed",
                    )
                summary = SourceSummary(
                    source_id=source_id,
                    title=candidate["title"],
                    origin_url=page.original_url,
                    state="available",
                    snapshot_hash=digest(text),
                    obtained_at=datetime.now(timezone.utc),
                    preview=text[:500],
                )
                passages = []
                for chunk, vector in zip(chunks, vectors):
                    locator = chunk.locator.model_copy(
                        update={"kind": "html_extracted_snapshot"}
                    )
                    passages.append(
                        TemporaryPassage(
                            source_id,
                            digest(text),
                            page.original_url,
                            candidate["title"],
                            chunk.text,
                            locator,
                            self.provider.validate_vector(vector),
                        )
                    )
                snapshots.append(
                    Snapshot(
                        summary,
                        text,
                        hashlib.sha256(page.body).hexdigest(),
                        pipeline_fingerprint(self.settings),
                        extraction,
                        page.effective_url,
                        passages,
                        self.settings.embedding_profile,
                    )
                )
            except AppError as error:
                errors.append(error.code)
                unavailable.append(
                    SourceSummary(
                        source_id=source_id,
                        title=candidate["title"],
                        origin_url=candidate["url"],
                        state="unavailable",
                        error_code=error.code,
                    )
                )
            except Exception:
                errors.append("SOURCE_PROCESSING_FAILED")
                unavailable.append(
                    SourceSummary(
                        source_id=source_id,
                        title=candidate["title"],
                        origin_url=candidate["url"],
                        state="unavailable",
                        error_code="SOURCE_PROCESSING_FAILED",
                    )
                )
        annotate(
            count=len(snapshots),
            error_count=len(errors),
            status="partial"
            if snapshots and errors
            else "succeeded"
            if snapshots
            else "failed"
            if errors
            else "empty",
        )
        capture_content(
            outputs={
                "sources": [s.summary.model_dump(mode="json") for s in snapshots],
                "unavailable": [s.model_dump(mode="json") for s in unavailable],
            }
        )
        return snapshots, unavailable, errors
