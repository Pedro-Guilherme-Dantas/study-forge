"""Runs labeled deterministic boundary cases. Semantic review is explicitly separate."""

import json
import subprocess
import sys
from pathlib import Path


def main():
    cases = [
        json.loads(line)
        for line in (Path(__file__).parent / "agent_cases.jsonl")
        .read_text(encoding="utf-8-sig")
        .splitlines()
    ]
    nodes = list(dict.fromkeys(case["test"] for case in cases))
    print(
        f"{len(cases)} casos rotulados; {len(nodes)} verificações selecionadas. Fixtures, sem geração real.",
        flush=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *nodes],
        check=False,
    )
    print(
        "Este runner não avalia semântica real; consulte evidence/E6-agents.md para a rodada Gemini separada.",
        flush=True,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
