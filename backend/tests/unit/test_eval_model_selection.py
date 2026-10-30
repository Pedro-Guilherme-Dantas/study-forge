"""The default experiment must not silently add an unselected generation model."""

from app.agents.tutor import TutorOutput
from app.settings import Settings
from evals import gemini_external


async def test_generation_defaults_only_to_the_configured_model(monkeypatch, capsys):
    models = []

    class Provider:
        last_generation_metadata = {}

        def __init__(self, settings):
            models.append(settings.gemini_generation_model)

    class Tutor:
        def __init__(self, *args):
            pass

        async def teach(self, *args):
            return TutorOutput(
                answer_markdown="Definição de ensaio [e1].",
                evidence_status="supported",
                citation_ids=["e1"],
            )

    monkeypatch.setattr(gemini_external, "GeminiProvider", Provider)
    monkeypatch.setattr(gemini_external, "Tutor", Tutor)
    monkeypatch.setattr(
        gemini_external,
        "CASES",
        [("own", "Pergunta autoral", ["Definição de ensaio."], "supported")],
    )
    await gemini_external.generation(
        Settings(gemini_generation_model="configured-only"), repetitions=1
    )
    assert models == ["configured-only"]
    assert '"successful": 1' in capsys.readouterr().out
