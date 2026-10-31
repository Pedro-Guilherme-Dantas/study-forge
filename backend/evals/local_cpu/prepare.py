"""Export the exact licensed baseline chunks and existing scoring functions."""

import hashlib
import inspect
import json
from pathlib import Path

from app.ingestion.chunk import chunk_text, pipeline_fingerprint
from app.ingestion.normalize import normalize
from app.settings import Settings
from evals.retrieval import metrics
from evals.web_retrieval import coverage, passage_metrics


def main():
    root = Path(__file__).resolve().parents[1]
    target = root / ".cache/local-comparison"
    target.mkdir(parents=True, exist_ok=True)
    baseline_path = root / "results/web-768-blocks-1600.json"
    baseline = json.loads(baseline_path.read_text())
    manifest = json.loads((root / "corpus/manifest.json").read_text())
    settings = Settings(app_mode="fixture", gemini_api_key="", search_api_key="")
    assert pipeline_fingerprint(settings) == baseline["pipeline_fingerprint"]
    chunks, documents = [], {}
    for entry in manifest["documents"]:
        body = (root / "corpus" / entry["file"]).read_text()
        assert hashlib.sha256(body.encode()).hexdigest() == entry["sha256"]
        document = normalize(body)
        documents[entry["id"]] = {
            "characters": len(body),
            "sha256": entry["sha256"],
            "original_lines": document.original_lines,
        }
        for chunk in chunk_text(document, settings):
            chunks.append(
                {
                    "document_id": entry["id"],
                    "text": chunk.text,
                    "chunk_id": chunk.sha256,
                    "section_path": chunk.locator.section_path,
                    "start_char": chunk.locator.start_char,
                    "end_char": chunk.locator.end_char,
                    "start_line": chunk.locator.start_line,
                    "end_line": chunk.locator.end_line,
                    "spans": document.spans[chunk.start : chunk.end],
                }
            )
    identities = {
        (row["document_id"], row["chunk_id"], row["start_char"], row["end_char"])
        for row in chunks
    }
    assert len(chunks) == baseline["chunks"]
    for case in baseline["results"]:
        for row in case["top_matches"]:
            assert (
                row["document_id"],
                row["chunk_id"],
                row["start_char"],
                row["end_char"],
            ) in identities
    cases_path = root / "retrieval_cases.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text().splitlines()]
    assert [case["id"] for case in cases] == [
        case["id"] for case in baseline["results"]
    ]
    payload = {
        "documents": documents,
        "chunks": chunks,
        "cases": cases,
        "baseline": baseline,
        "baseline_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
        "labels_sha256": hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        "pipeline_fingerprint": baseline["pipeline_fingerprint"],
    }
    (target / "input.json").write_text(json.dumps(payload, ensure_ascii=False))
    scoring = "import statistics\n\n" + "\n\n".join(
        inspect.getsource(function) for function in (metrics, coverage, passage_metrics)
    )
    (target / "evaluation_metrics.py").write_text(scoring)
    print(
        json.dumps(
            {
                "documents": len(documents),
                "chunks": len(chunks),
                "questions": len(cases),
                "baseline_identities_verified": True,
            }
        )
    )


if __name__ == "__main__":
    main()
