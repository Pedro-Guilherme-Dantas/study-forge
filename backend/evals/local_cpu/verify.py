"""Check batching/padding invariance and token-window coverage using the real model."""

import json
from pathlib import Path

from run import BATCH, LIMIT, THREADS, bounded_chunks, prefix
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

data = json.loads(Path("/data/input.json").read_text())
tokenizer = Tokenizer.from_file("/models/onnx/tokenizer.json")
for parent in data["chunks"]:
    children = bounded_chunks([parent], tokenizer, data["documents"])
    assert "".join(child["text"] for child in children) == parent["text"]
    assert [span for child in children for span in child["spans"]] == parent["spans"]
    assert all(len(tokenizer.encode(prefix(child) + child["text"]).ids) <= LIMIT for child in children)

options = ort.SessionOptions()
options.intra_op_num_threads, options.inter_op_num_threads = THREADS, 1
session = ort.InferenceSession("/models/onnx/model.onnx", sess_options=options, providers=["CPUExecutionProvider"])
names = {value.name for value in session.get_inputs()}
tokenizer.enable_truncation(max_length=LIMIT)


def encode(texts, pad):
    tokenizer.enable_padding(pad_id=pad, pad_token=tokenizer.id_to_token(pad))
    encoded = tokenizer.encode_batch(texts)
    inputs = {
        "input_ids": np.array([value.ids for value in encoded], dtype=np.int64),
        "attention_mask": np.array([value.attention_mask for value in encoded], dtype=np.int64),
        "token_type_ids": np.array([value.type_ids for value in encoded], dtype=np.int64),
    }
    hidden = session.run(None, {key: value for key, value in inputs.items() if key in names})[0]
    mask = inputs["attention_mask"][..., None]
    pooled = (hidden * mask).sum(axis=1) / mask.sum(axis=1)
    return pooled / np.linalg.norm(pooled, axis=1, keepdims=True)


texts = ["query: " + data["cases"][0]["question"]] + [prefix(data["chunks"][i]) + data["chunks"][i]["text"] for i in (0, 1, 40, 80, 120, 200, 300)]
pad = json.loads(Path("/models/config.json").read_text())["pad_token_id"]
single = np.stack([encode([value], pad)[0] for value in texts])
batch = encode(texts, pad)
alternate_padding = encode(texts, tokenizer.token_to_id("<pad>"))
batch_cosine = float(np.min(np.sum(single * batch, axis=1)))
padding_cosine = float(np.min(np.sum(batch * alternate_padding, axis=1)))
assert batch_cosine > .9999 and padding_cosine > .9999
old = json.loads(Path("/results/local-e5-small-comparison-run1.json").read_text())
new = json.loads(Path("/results/local-e5-small-comparison.json").read_text())
assert all(a["aggregate"] == b["aggregate"] for a, b in zip(old["variants"], new["variants"], strict=True))
report = {"token_partition_no_content_loss": True, "adapted_token_limit_verified": LIMIT, "batch_samples": len(texts), "minimum_single_vs_batch_cosine": batch_cosine, "minimum_padding_id_cosine": padding_cosine, "repeated_aggregate_metrics_identical": True}
Path("/results/local-e5-small-verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
