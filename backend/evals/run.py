"""Fixture-only baseline. Does not write evaluation content into the personal library."""

import json
from pathlib import Path
from app.providers.gemini import GeminiProvider
from app.settings import Settings
from evals.retrieval import metrics


def main():
    root = Path(__file__).parent
    manifest = json.loads(
        (root / "corpus/manifest.json").read_text(encoding="utf-8-sig")
    )
    provider = GeminiProvider(Settings(app_mode="fixture"))
    corpus = [
        (
            doc["id"],
            provider._fixture_vector(
                (root / "corpus" / doc["file"]).read_text(encoding="utf-8-sig")
            ),
        )
        for doc in manifest["documents"]
    ]
    results = []
    for line in (
        (root / "retrieval_cases.jsonl").read_text(encoding="utf-8-sig").splitlines()
    ):
        case = json.loads(line)
        query = provider._fixture_vector(case["question"])
        ranking = [
            key
            for key, vector in sorted(
                corpus,
                key=lambda item: (-sum(a * b for a, b in zip(item[1], query)), item[0]),
            )
        ]
        results.append(
            {
                "case": case["id"],
                "ranking": ranking[:8],
                **metrics(ranking, case["relevant_documents"]),
            }
        )
    print(
        json.dumps(
            {
                "profile": "fixture-hash-v1:768",
                "semantic_model_evaluation": False,
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
