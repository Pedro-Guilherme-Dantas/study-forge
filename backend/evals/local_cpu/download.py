"""Download only pinned, public model artifacts; no execution of remote Python."""

import json
from pathlib import Path
import time
import urllib.request

MODEL = "intfloat/multilingual-e5-small"
REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"


def event(name, **values):
    print(json.dumps({"event": name, **values}), flush=True)


def download(name):
    path = Path("/models") / name
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        f"https://huggingface.co/{MODEL}/resolve/{REVISION}/{name}",
        headers={"User-Agent": "StudyForge-authorized-local-eval/1.0"},
    )
    size, announced = 0, 0
    part = path.with_suffix(path.suffix + ".part")
    with (
        urllib.request.urlopen(request, timeout=120) as response,
        part.open("wb") as output,
    ):
        while block := response.read(1024 * 1024):
            size += len(block)
            if size > 800_000_000:
                raise ValueError("Model artifact exceeded the experiment limit")
            output.write(block)
            if size - announced >= 64 * 1024 * 1024:
                event("download_progress", artifact=name, mib=round(size / 1024**2))
                announced = size
    part.replace(path)
    event("download_complete", artifact=name, bytes=size)
    return path


if __name__ == "__main__":
    started = time.perf_counter()
    try:
        for filename in ("config.json", "onnx/tokenizer.json", "onnx/model.onnx"):
            download(filename)
        report = {
            "seconds": round(time.perf_counter() - started, 3),
            "model": MODEL,
            "revision": REVISION,
        }
        Path("/models/download-info.json").write_text(json.dumps(report))
        event("model_download_finished", **report)
    except Exception as error:
        event(
            "failed",
            error_type=type(error).__name__,
            status=getattr(error, "code", None),
        )
        raise SystemExit(1)
