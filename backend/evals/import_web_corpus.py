"""Reproducible, explicitly user-authorized evaluation import, independent of the product library.

Wikipedia text is redistributed under CC BY-SA 4.0 with page/history/revision attribution.
Images and third-party media are not imported. Runtime research never calls this script.
"""

import hashlib
import json
import re
import shutil
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PAGES = [
    ("celula", "Célula"),
    ("fotossintese", "Fotossíntese"),
    ("mitose", "Mitose"),
    ("gravidade", "Gravitação"),
    ("inercia", "Inércia"),
    ("energia", "Lei da conservação da energia"),
    ("fracao", "Fração"),
    ("primo", "Número primo"),
    ("media", "Média aritmética"),
    ("algoritmo", "Algoritmo"),
    ("transacao", "Transação (banco de dados)"),
    ("evidencia", "Método científico"),
]
ROOT = Path(__file__).parent / "corpus"


def main():
    backup = ROOT / "synthetic"
    if not backup.exists():
        backup.mkdir()
        for path in ROOT.glob("*.md"):
            shutil.copyfile(path, backup / path.name)
        shutil.copyfile(ROOT / "manifest.json", backup / "manifest.json")
        shutil.copyfile(
            ROOT.parent / "retrieval_cases.jsonl", backup / "retrieval_cases.jsonl"
        )
    documents = []
    contents = {}
    for identifier, title in PAGES:
        params = {
            "action": "query",
            "prop": "extracts|info|revisions",
            "titles": title,
            "explaintext": "1",
            "inprop": "url",
            "rvprop": "ids",
            "redirects": "1",
            "format": "json",
        }
        url = "https://pt.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "StudyForge/0.1 (local educational retrieval evaluation)"
            },
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    payload = json.load(response)
                break
            except OSError:
                if attempt == 2:
                    raise
                time.sleep(attempt + 1)
        page = next(iter(payload["query"]["pages"].values()))
        if "missing" in page or not page.get("extract"):
            raise ValueError("Page unavailable: " + title)
        body = page["extract"]
        body = re.sub(
            r"(?m)^(={2,6})\s*(.+?)\s*\1\s*$",
            lambda match: "#" * len(match[1]) + " " + match[2],
            body,
        )
        markdown = "# " + page["title"] + "\n\n" + body.strip() + "\n"
        contents[identifier] = markdown
        revision = page["revisions"][0]["revid"]
        record = {
            "id": identifier,
            "file": identifier + ".md",
            "title": page["title"],
            "source_url": page["fullurl"],
            "revision_id": revision,
            "revision_url": f"https://pt.wikipedia.org/w/index.php?oldid={revision}",
            "authors": "Colaboradores da Wikipédia",
            "authors_url": page["fullurl"] + "?action=history",
            "license": "CC-BY-SA-4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "characters": len(markdown),
            "words": len(markdown.split()),
            "sha256": hashlib.sha256(markdown.encode()).hexdigest(),
            "modifications": "API plaintext extract converted to Markdown headings; no summary; media excluded.",
        }
        documents.append(record)
        print(
            json.dumps(
                {
                    "id": identifier,
                    "title": page["title"],
                    "characters": len(markdown),
                    "words": record["words"],
                    "revision": revision,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        time.sleep(0.2)
    for identifier, markdown in contents.items():
        (ROOT / (identifier + ".md")).write_text(markdown, encoding="utf-8")
    (ROOT / "manifest.json").write_text(
        json.dumps(
            {
                "provenance": "Web corpus explicitly requested by the user; Wikipedia extracts, not synthetic prose.",
                "license_notice": "NOTICE.md",
                "documents": documents,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    notice = [
        "# Atribuição e licença do corpus web\n",
        "Textos: colaboradores da Wikipédia em português. CC BY-SA 4.0.",
        "Licença: https://creativecommons.org/licenses/by-sa/4.0/",
        "Reuso: https://foundation.wikimedia.org/wiki/Terms_of_Use#7._Licensing_of_Content",
        "Conversão: extratos textuais completos da API com títulos convertidos para Markdown; imagens/mídia excluídas. Os textos não foram resumidos.",
        "As adaptações desses textos permanecem sob CC BY-SA 4.0. Essa licença refere-se ao corpus, não impõe uma licença ao código da aplicação.",
        "Os textos servem para avaliar recuperação e não constituem validação científica ou pedagógica do produto.",
        "\n## Fontes\n",
    ]
    for doc in documents:
        notice.append(
            f"- [{doc['title']}]({doc['revision_url']}) — [autores/histórico]({doc['authors_url']}), revisão {doc['revision_id']}, arquivo `{doc['file']}`."
        )
    (ROOT / "NOTICE.md").write_text("\n\n".join(notice) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
