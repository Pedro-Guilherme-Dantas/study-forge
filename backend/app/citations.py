"""The application resolves citations; model text never creates source identities."""

from dataclasses import dataclass
from app.errors import AppError
from app.schemas import LibraryCitation, TemporaryCitation


@dataclass
class EvidenceSet:
    items: dict

    @classmethod
    def from_results(cls, results):
        return cls({f"e{index + 1}": item for index, item in enumerate(results)})

    def resolve(self, references, prefix):
        citations = []
        seen = set()
        for reference in references:
            if reference in seen:
                continue
            seen.add(reference)
            if reference not in self.items:
                raise AppError(
                    "INVALID_CITATION",
                    "A resposta citou uma fonte indisponível.",
                    502,
                    "citation",
                )
            passage = self.items[reference].passage
            if hasattr(passage, "source_id"):
                citations.append(
                    TemporaryCitation(
                        citation_id=f"{prefix}-{reference}",
                        title=passage.display_name,
                        quote=passage.text,
                        locator=passage.locator,
                        source_id=passage.source_id,
                        snapshot_hash=passage.snapshot_hash,
                        origin_url=passage.origin_url,
                    )
                )
                continue
            citations.append(
                LibraryCitation(
                    citation_id=f"{prefix}-{reference}",
                    title=passage.display_name,
                    quote=passage.text,
                    locator=passage.locator,
                    material_id=passage.material_id,
                    version_id=passage.version_id,
                    chunk_id=passage.chunk_id,
                )
            )
        return citations
