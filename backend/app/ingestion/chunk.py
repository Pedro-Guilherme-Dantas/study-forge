from dataclasses import dataclass
import hashlib
import json
import unicodedata
from importlib.metadata import version
from app.errors import AppError
from app.schemas import Locator
from app.settings import Settings
from app.ingestion.normalize import Document


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pipeline_config(settings: Settings):
    return {
        "version": "text-v1",
        "normalizer": "NFC-LF-BOM-v1",
        "unicode": unicodedata.unidata_version,
        "parser": version("markdown-it-py"),
        "graphemes": version("regex"),
        "html": False,
        "chunker": "contiguous-blocks-v1",
        "target": settings.chunk_target,
        "max": settings.chunk_max,
        "overlap": settings.chunk_overlap,
    }


def pipeline_fingerprint(settings: Settings):
    return digest(
        json.dumps(pipeline_config(settings), sort_keys=True, separators=(",", ":"))
    )


@dataclass(frozen=True)
class TextChunk:
    text: str
    start: int
    end: int
    locator: Locator
    sha256: str


def chunk_text(doc: Document, settings: Settings, kind="markdown_original"):
    chunks, start = [], 0
    length = len(doc.text)
    while start < length:
        if len(chunks) >= 2048:
            raise AppError(
                "EXECUTION_LIMIT",
                "O material excede o limite de trechos.",
                429,
                "chunk",
            )
        maximum = min(length, start + settings.chunk_max)
        candidates = [b.end for b in doc.blocks if start < b.end <= maximum]
        near = [point for point in candidates if point >= start + settings.chunk_target]
        end = near[0] if near else (candidates[-1] if candidates else maximum)
        if end < length and end == maximum:
            newline = doc.text.rfind("\n", start + 1, end)
            if newline > start:
                end = newline + 1
        while end < length and end > start and doc.spans[end - 1] == doc.spans[end]:
            end -= 1
        if end <= start:
            raise AppError(
                "EXECUTION_LIMIT",
                "Bloco Unicode excede o limite de trecho.",
                429,
                "chunk",
            )
        text = doc.text[start:end]
        if text.strip():
            block = next(
                (b for b in doc.blocks if b.start <= start < b.end),
                next((b for b in doc.blocks if b.start >= start), None),
            )
            first, last, line1, line2 = doc.source_range(start, end)
            locator = Locator(
                kind=kind,
                section_path=list(block.section) if block else [],
                start_char=first,
                end_char=last,
                start_line=line1,
                end_line=line2,
                block_index=block.index if block else 0,
            )
            chunks.append(TextChunk(text, start, end, locator, digest(text)))
        overlap_starts = [
            b.start
            for b in doc.blocks
            if max(start + 1, end - settings.chunk_overlap) <= b.start < end
        ]
        start = overlap_starts[0] if overlap_starts and end < length else end
    return chunks
