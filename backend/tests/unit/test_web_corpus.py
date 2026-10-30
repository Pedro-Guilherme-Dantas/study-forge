import hashlib
import json
from pathlib import Path
from evals.web_retrieval import coverage, passage_metrics


def test_downloaded_corpus_identity_license_size_and_labels():
    root = Path("evals/corpus")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8-sig"))
    assert len(manifest["documents"]) == 12
    texts = {}
    for doc in manifest["documents"]:
        body = (root / doc["file"]).read_text()
        texts[doc["id"]] = body
        assert (
            len(body) >= 12000
            and doc["sha256"] == hashlib.sha256(body.encode()).hexdigest()
        )
        assert (
            doc["license"] == "CC-BY-SA-4.0"
            and doc["revision_id"]
            and doc["authors_url"]
        )
    cases = [
        json.loads(line)
        for line in Path("evals/retrieval_cases.jsonl").read_text().splitlines()
    ]
    assert len(cases) == 32 and sum(case["unanswerable"] for case in cases) == 4
    for case in cases:
        for anchor in case["evidence"]:
            assert (
                texts[anchor["document_id"]][anchor["start_char"] : anchor["end_char"]]
                == anchor["quote"]
            )


def test_passage_coverage_counts_union_without_overlap_inflation():
    assert coverage([(0, 7), (5, 12)], 0, 10) == 1
    assert coverage([(0, 5), (0, 5)], 0, 10) == 0.5
    evidence = [{"document_id": "a", "start_char": 0, "end_char": 10}]
    ranked = [
        {"document_id": "a", "start_char": 0, "end_char": 6},
        {"document_id": "a", "start_char": 6, "end_char": 10},
    ]
    result = passage_metrics(ranked, evidence)
    assert result["passage_recall@3"] == 1 and result["passage_mrr"] == 0
