"""CPU-only E5 experiment: exact baseline chunks and an explicitly token-bounded variant."""

import bisect
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import statistics
import sys
import time

import numpy as np
import onnxruntime as ort
import psycopg
from tokenizers import Tokenizer
from download import MODEL, REVISION, download, event

ort.disable_telemetry_events()

sys.path.insert(0, "/data")
from evaluation_metrics import metrics, passage_metrics

THREADS = 4
BATCH = 8
LIMIT = 512


def rss_mib():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2)


def prefix(chunk):
    return "passage: " + " / ".join(chunk["section_path"]) + "\n"


def bounded_chunks(chunks, tokenizer, documents):
    result = []
    for parent in chunks:
        heading = prefix(parent)
        if len(tokenizer.encode(heading + parent["text"]).ids) <= LIMIT:
            result.append(parent)
            continue
        start = 0
        while start < len(parent["text"]):
            left, right, end = start + 1, len(parent["text"]), start
            while left <= right:
                middle = (left + right) // 2
                if (
                    len(tokenizer.encode(heading + parent["text"][start:middle]).ids)
                    <= LIMIT
                ):
                    end, left = middle, middle + 1
                else:
                    right = middle - 1
            while (
                start < end < len(parent["text"])
                and parent["spans"][end - 1] == parent["spans"][end]
            ):
                end -= 1
            if end <= start:
                raise ValueError("Heading or grapheme does not fit token budget")
            child = dict(parent)
            child["text"] = parent["text"][start:end]
            child["spans"] = parent["spans"][start:end]
            child["chunk_id"] = hashlib.sha256(child["text"].encode()).hexdigest()
            child["start_char"], child["end_char"] = (
                child["spans"][0][0],
                child["spans"][-1][1],
            )
            lines = documents[child["document_id"]]["original_lines"]
            child["start_line"] = bisect.bisect_right(lines, child["start_char"])
            child["end_line"] = bisect.bisect_right(lines, child["end_char"] - 1)
            assert len(tokenizer.encode(heading + child["text"]).ids) <= LIMIT
            result.append(child)
            start = end
    return result


def aggregate(results):
    rows = [row for row in results if row["expected_documents"]]
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
    return (
        {field: statistics.mean(row[field] for row in rows) for field in fields},
        {
            kind: {
                field: statistics.mean(
                    row[field] for row in rows if row["kind"] == kind
                )
                for field in fields
            }
            for kind in ("section", "cross_document")
        },
    )


def evaluate(chunks, vectors, cases, queries):
    results = []
    with psycopg.connect(os.environ["EVAL_DATABASE_URL"]) as db:
        db.execute("SET statement_timeout='30s'")
        db.execute(
            "CREATE TEMP TABLE local_eval_vectors (id integer, document text, embedding vector(384)) ON COMMIT DROP"
        )
        with db.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO local_eval_vectors VALUES (%s,%s,%s::vector)",
                [
                    (i, chunk["document_id"], json.dumps(vector.tolist()))
                    for i, (chunk, vector) in enumerate(
                        zip(chunks, vectors, strict=True)
                    )
                ],
            )
        for case, query in zip(cases, queries, strict=True):
            ranked = []
            for index, document, distance in db.execute(
                "SELECT id,document,embedding <=> %s::vector AS distance FROM local_eval_vectors ORDER BY distance,id LIMIT 8",
                (json.dumps(query.tolist()),),
            ):
                chunk = chunks[index]
                ranked.append(
                    {
                        key: chunk[key]
                        for key in (
                            "document_id",
                            "chunk_id",
                            "start_char",
                            "end_char",
                            "start_line",
                            "end_line",
                            "section_path",
                        )
                    }
                )
                ranked[-1].update(
                    cosine_similarity=round(1 - distance, 6),
                    excerpt=chunk["text"][:300],
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
    return results


def main():
    data = json.loads(Path("/data/input.json").read_text())
    started = time.perf_counter()
    event(
        "setup",
        model=MODEL,
        revision=REVISION,
        provider="CPUExecutionProvider",
        threads=THREADS,
        batch=BATCH,
    )
    files = {
        name: download(name)
        for name in ("config.json", "onnx/tokenizer.json", "onnx/model.onnx")
    }
    download_seconds = time.perf_counter() - started
    started = time.perf_counter()
    tokenizer = Tokenizer.from_file(str(files["onnx/tokenizer.json"]))
    pad = json.loads(files["config.json"].read_text())["pad_token_id"]
    options = ort.SessionOptions()
    options.intra_op_num_threads, options.inter_op_num_threads = THREADS, 1
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(
        str(files["onnx/model.onnx"]),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )
    load_seconds = time.perf_counter() - started
    with files["onnx/model.onnx"].open("rb") as model_file:
        model_hash = hashlib.file_digest(model_file, "sha256").hexdigest()
    document_tokens = [
        len(tokenizer.encode(prefix(chunk) + chunk["text"]).ids)
        for chunk in data["chunks"]
    ]
    adapted = bounded_chunks(data["chunks"], tokenizer, data["documents"])
    event(
        "token_budget",
        original_chunks=len(data["chunks"]),
        over_limit=sum(length > LIMIT for length in document_tokens),
        longest=max(document_tokens),
        adapted_chunks=len(adapted),
        load_seconds=round(load_seconds, 3),
        rss_mib=rss_mib(),
    )
    tokenizer.enable_truncation(max_length=LIMIT)
    tokenizer.enable_padding(pad_id=pad, pad_token=tokenizer.id_to_token(pad))
    input_names = {value.name for value in session.get_inputs()}

    def encode(texts):
        encoded = tokenizer.encode_batch(texts)
        inputs = {
            "input_ids": np.array([value.ids for value in encoded], dtype=np.int64),
            "attention_mask": np.array(
                [value.attention_mask for value in encoded], dtype=np.int64
            ),
            "token_type_ids": np.array(
                [value.type_ids for value in encoded], dtype=np.int64
            ),
        }
        hidden = session.run(
            None, {key: value for key, value in inputs.items() if key in input_names}
        )[0]
        mask = inputs["attention_mask"][..., None]
        pooled = (hidden * mask).sum(axis=1) / mask.sum(axis=1)
        pooled = pooled / np.linalg.norm(pooled, axis=1, keepdims=True)
        assert pooled.shape == (len(texts), 384) and np.isfinite(pooled).all()
        return pooled.astype(np.float32)

    query_texts = ["query: " + case["question"] for case in data["cases"]]
    started = time.perf_counter()
    encode([query_texts[0]])
    first_query_ms = (time.perf_counter() - started) * 1000
    queries, query_ms = [], []
    for repeat in range(2):
        for question in query_texts:
            started = time.perf_counter()
            value = encode([question])[0]
            query_ms.append((time.perf_counter() - started) * 1000)
            if repeat == 0:
                queries.append(value)
    reports = []
    for label, chunks in (
        ("same-chunks-1600-truncation-explicit", data["chunks"]),
        ("same-parent-chunks-token-bounded-512", adapted),
    ):
        started = time.perf_counter()
        vectors, document_times = [], []
        for document in data["documents"]:
            group = [chunk for chunk in chunks if chunk["document_id"] == document]
            document_started = time.perf_counter()
            for offset in range(0, len(group), BATCH):
                vectors.extend(
                    encode(
                        [
                            prefix(chunk) + chunk["text"]
                            for chunk in group[offset : offset + BATCH]
                        ]
                    )
                )
            seconds = time.perf_counter() - document_started
            document_times.append(
                {"id": document, "chunks": len(group), "seconds": round(seconds, 3)}
            )
            event(
                "document_encoded",
                variant=label,
                document=document,
                chunks=len(group),
                seconds=round(seconds, 3),
                rss_mib=rss_mib(),
            )
        encode_seconds = time.perf_counter() - started
        # Preserve the exact stable chunk order used in vectors and tie-breaking.
        ordered_chunks = [
            chunk
            for document in data["documents"]
            for chunk in chunks
            if chunk["document_id"] == document
        ]
        results = evaluate(ordered_chunks, vectors, data["cases"], queries)
        summary, by_kind = aggregate(results)
        changes = [
            {
                "id": row["id"],
                "question": row["question"],
                "gemini_passage_recall@5": old["passage_recall@5"],
                "local_passage_recall@5": row["passage_recall@5"],
                "delta": row["passage_recall@5"] - old["passage_recall@5"],
            }
            for row, old in zip(results, data["baseline"]["results"], strict=True)
            if row["expected_documents"]
            and row["passage_recall@5"] != old["passage_recall@5"]
        ]
        report = {
            "variant": label,
            "chunks": len(chunks),
            "truncated_inputs": sum(length > LIMIT for length in document_tokens)
            if label.startswith("same-chunks")
            else 0,
            "document_embedding_seconds": round(encode_seconds, 3),
            "documents_timing": document_times,
            "aggregate": summary,
            "by_kind": by_kind,
            "changed_cases": changes,
            "results": results,
            "peak_process_rss_mib": rss_mib(),
        }
        reports.append(report)
        event(
            "variant_complete",
            **{
                key: report[key]
                for key in (
                    "variant",
                    "chunks",
                    "document_embedding_seconds",
                    "aggregate",
                    "peak_process_rss_mib",
                )
            },
        )
    report = {
        "model": MODEL,
        "revision": REVISION,
        "onnx_sha256": model_hash,
        "dimensions": 384,
        "precision": "FP32",
        "runtime": "ONNX Runtime CPU",
        "threads": THREADS,
        "batch_size": BATCH,
        "token_limit": LIMIT,
        "prefixes": ["query: ", "passage: "],
        "pooling": "attention-masked mean + L2",
        "download_or_cache_lookup_seconds": round(download_seconds, 3),
        "load_seconds": round(load_seconds, 3),
        "first_query_after_load_ms": round(first_query_ms, 3),
        "warm_queries": {
            "samples": len(query_ms),
            "median_ms": round(statistics.median(query_ms), 3),
            "p95_ms": round(float(np.percentile(query_ms, 95)), 3),
            "maximum_ms": round(max(query_ms), 3),
        },
        "peak_process_rss_mib": rss_mib(),
        "cgroup_peak_mib": round(
            int(Path("/sys/fs/cgroup/memory.peak").read_text()) / 1024**2, 2
        ),
        "packages": {
            dist.metadata["Name"]: dist.version
            for dist in importlib.metadata.distributions()
        },
        "pipeline_fingerprint": data["pipeline_fingerprint"],
        "baseline_sha256": data["baseline_sha256"],
        "labels_sha256": data["labels_sha256"],
        "documents": len(data["documents"]),
        "questions": len(data["cases"]),
        "answerable": data["baseline"]["answerable"],
        "baseline_aggregate": data["baseline"]["aggregate"],
        "variants": reports,
    }
    Path("/results/local-e5-small-comparison.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    event(
        "complete",
        warm_queries=report["warm_queries"],
        peak_process_rss_mib=report["peak_process_rss_mib"],
        cgroup_peak_mib=report["cgroup_peak_mib"],
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        event(
            "failed",
            error_type=type(error).__name__,
            status=getattr(error, "code", None),
        )
        raise SystemExit(1)
