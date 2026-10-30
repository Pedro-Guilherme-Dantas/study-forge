"""Actual pgvector retrieval over the licensed, user-selected long-document corpus.

Only evaluation material is written to temporary SQL tables. The personal library is untouched.
"""

import asyncio
import json
import os
import statistics
import time
import argparse
from pathlib import Path
from sqlalchemy import create_engine, text
from app.settings import Settings
from app.diagnostics import configure
from app.ingestion.normalize import normalize
from app.ingestion.chunk import chunk_text, pipeline_fingerprint
from evals.gemini_external import embed_batch
from evals.retrieval import metrics

ROOT = Path(__file__).parent


def coverage(intervals, start, end):
    pieces = sorted(
        (max(a, start), min(b, end)) for a, b in intervals if b > start and a < end
    )
    covered = 0
    last = start
    for left, right in pieces:
        covered += max(0, right - max(last, left))
        last = max(last, right)
    return covered / (end - start)


def passage_metrics(ranked, evidence):
    if not evidence:
        return {}
    result = {}
    for k in (3, 5, 8):
        fractions = [
            coverage(
                [
                    (row["start_char"], row["end_char"])
                    for row in ranked[:k]
                    if row["document_id"] == anchor["document_id"]
                ],
                anchor["start_char"],
                anchor["end_char"],
            )
            for anchor in evidence
        ]
        result[f"passage_recall@{k}"] = sum(value >= 1 for value in fractions) / len(
            fractions
        )
        result[f"span_coverage@{k}"] = statistics.mean(fractions)
    result["passage_mrr"] = next(
        (
            1 / index
            for index, row in enumerate(ranked, 1)
            if any(
                row["document_id"] == anchor["document_id"]
                and row["start_char"] <= anchor["start_char"]
                and row["end_char"] >= anchor["end_char"]
                for anchor in evidence
            )
        ),
        0,
    )
    return result


async def run(dimensions_to_test=(768, 1536), targets=(1600, 800), pause_seconds=0):
    configure()
    settings = Settings(app_mode="real")
    manifest = json.loads(
        (ROOT / "corpus/manifest.json").read_text(encoding="utf-8-sig")
    )
    documents = {
        doc["id"]: normalize(
            (ROOT / "corpus" / doc["file"]).read_text(encoding="utf-8-sig")
        )
        for doc in manifest["documents"]
    }
    cases = [
        json.loads(line)
        for line in (ROOT / "retrieval_cases.jsonl").read_text().splitlines()
    ]
    engine = create_engine(os.environ["TEST_DATABASE_URL"], hide_parameters=True)
    reports = []
    try:
        cache = ROOT / ".cache" / "authorized-web-corpus-only"
        for dimensions in dimensions_to_test:
            query_vectors = await embed_batch(
                settings,
                [case["question"] for case in cases],
                dimensions,
                True,
                cache,
                pause_seconds,
            )
            for target in targets:
                label = f"blocks-{target}"
                config = (
                    settings
                    if target == 1600
                    else settings.model_copy(
                        update={
                            "chunk_target": target,
                            "chunk_max": int(target * 1.5),
                            "chunk_overlap": target // 8,
                        }
                    )
                )
                started = time.monotonic()
                chunks = [
                    (document, chunk)
                    for document, body in documents.items()
                    for chunk in chunk_text(body, config)
                ]
                print(
                    json.dumps(
                        {
                            "event": "embedding_documents",
                            "dimensions": dimensions,
                            "chunking": label,
                            "chunks": len(chunks),
                        }
                    ),
                    flush=True,
                )
                vectors = await embed_batch(
                    settings,
                    [
                        " / ".join(chunk.locator.section_path) + "\n" + chunk.text
                        for _, chunk in chunks
                    ],
                    dimensions,
                    False,
                    cache,
                    pause_seconds,
                )
                results = []
                with engine.begin() as db:
                    db.execute(
                        text(
                            f"CREATE TEMP TABLE eval_web_vectors (id integer,document text,embedding vector({dimensions})) ON COMMIT DROP"
                        )
                    )
                    db.execute(
                        text(
                            "INSERT INTO eval_web_vectors VALUES (:id,:document,CAST(:vector AS vector))"
                        ),
                        [
                            {
                                "id": index,
                                "document": document,
                                "vector": json.dumps(vector),
                            }
                            for index, ((document, _), vector) in enumerate(
                                zip(chunks, vectors)
                            )
                        ],
                    )
                    for case, query in zip(cases, query_vectors):
                        rows = db.execute(
                            text(
                                "SELECT id,document,embedding <=> CAST(:vector AS vector) AS distance FROM eval_web_vectors ORDER BY distance,id LIMIT 8"
                            ),
                            {"vector": json.dumps(query)},
                        ).all()
                        ranked = []
                        for row in rows:
                            document, chunk = chunks[row.id]
                            ranked.append(
                                {
                                    "document_id": document,
                                    "chunk_id": chunk.sha256,
                                    "start_char": chunk.locator.start_char,
                                    "end_char": chunk.locator.end_char,
                                    "start_line": chunk.locator.start_line,
                                    "end_line": chunk.locator.end_line,
                                    "section_path": chunk.locator.section_path,
                                    "cosine_similarity": round(1 - row.distance, 6),
                                    "excerpt": chunk.text[:300],
                                }
                            )
                        results.append(
                            {
                                "id": case["id"],
                                "kind": case["kind"],
                                "question": case["question"],
                                "expected_documents": case["relevant_documents"],
                                **metrics(
                                    [row["document_id"] for row in ranked],
                                    case["relevant_documents"],
                                ),
                                **passage_metrics(ranked, case["evidence"]),
                                "top_matches": ranked,
                            }
                        )
                answerable = [
                    result for result in results if result["expected_documents"]
                ]
                fields = (
                    "recall@3",
                    "recall@5",
                    "recall@8",
                    "mrr",
                    "passage_recall@3",
                    "passage_recall@5",
                    "passage_recall@8",
                    "span_coverage@5",
                    "passage_mrr",
                )
                aggregate = {
                    field: statistics.mean(row[field] for row in answerable)
                    for field in fields
                }
                by_kind = {
                    kind: {
                        field: statistics.mean(
                            row[field] for row in answerable if row["kind"] == kind
                        )
                        for field in fields
                    }
                    for kind in ("section", "cross_document")
                }
                report = {
                    "experiment": "web-corpus-E3",
                    "provider": "Gemini Developer API",
                    "embedding_model": settings.gemini_embedding_model,
                    "dimensions": dimensions,
                    "chunking": label,
                    "embedding_batch_size": settings.embedding_batch_size,
                    "pipeline_fingerprint": pipeline_fingerprint(config),
                    "documents": len(documents),
                    "characters": sum(len(doc.original) for doc in documents.values()),
                    "chunks": len(chunks),
                    "questions": len(cases),
                    "answerable": len(answerable),
                    "unanswerable": len(cases) - len(answerable),
                    "seconds": round(time.monotonic() - started, 3),
                    "aggregate": aggregate,
                    "by_kind": by_kind,
                    "results": results,
                    "limitations": [
                        "Proposed manual anchors, not exhaustive relevance judgments.",
                        "No universal similarity cutoff; unanswerable cases excluded from recall.",
                        "Source text uses CC BY-SA 4.0; see corpus/NOTICE.md.",
                    ],
                }
                reports.append(report)
                target = ROOT / "results"
                target.mkdir(exist_ok=True)
                (target / f"web-{dimensions}-{label}.json").write_text(
                    json.dumps(report, ensure_ascii=False, indent=2) + "\n"
                )
                print(
                    json.dumps(
                        {
                            key: value
                            for key, value in report.items()
                            if key not in ("results", "by_kind", "limitations")
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
    finally:
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dimensions", type=int, nargs="+", default=[768, 1536])
    parser.add_argument("--chunk-targets", type=int, nargs="+", default=[1600, 800])
    parser.add_argument("--pause-seconds", type=float, default=0)
    args = parser.parse_args()
    try:
        asyncio.run(run(args.dimensions, args.chunk_targets, args.pause_seconds))
    except Exception as error:
        print(
            json.dumps(
                {
                    "experiment": "web-corpus-E3",
                    "ok": False,
                    "error_type": type(error).__name__,
                    "status": getattr(error, "code", None),
                }
            )
        )
        raise SystemExit(1)
