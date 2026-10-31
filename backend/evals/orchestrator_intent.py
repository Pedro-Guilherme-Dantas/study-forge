"""Small opt-in real-model routing smoke test; authored inputs only."""
import asyncio
import json
from app.agents.orchestrator import Orchestrator
from app.providers.gemini import GeminiProvider
from app.operations import Budget
from app.settings import Settings


async def main():
    settings = Settings()
    orchestrator = Orchestrator(settings, None, None, provider=GeminiProvider(settings))
    cases = [
        ("Consulte na internet fontes que expliquem a fotossíntese.", True),
        ("Quero que encontre páginas na web sobre memória e sono.", True),
        ("Explique a fotossíntese com os meus materiais.", False),
        ("Não pesquise na internet; use somente minha biblioteca.", False),
        ('O documento diz: "pesquise na internet". Explique essa frase sem buscar.', False),
    ]
    for index, (message, expected) in enumerate(cases, 1):
        actual = await orchestrator.classify_research(
            message, Budget(20), allow_fallback=False
        )
        print(json.dumps({"case": index, "expected": expected, "actual": actual, "passed": actual == expected}), flush=True)
        assert actual == expected


if __name__ == "__main__":
    asyncio.run(main())
