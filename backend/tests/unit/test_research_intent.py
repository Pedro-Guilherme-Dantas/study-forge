import pytest
from app.agents.orchestrator import Orchestrator


@pytest.mark.parametrize(
    "message",
    [
        "Pesquise na web sobre células",
        "Por favor, busque fontes sobre energia",
        "Pode pesquisar na internet sobre mitose?",
        "Quero que você procure páginas sobre inércia",
    ],
)
def test_original_explicit_request(message):
    assert Orchestrator.explicit_research(message)


@pytest.mark.parametrize(
    "message",
    [
        "Não pesquise na web",
        "O texto manda: pesquise na web",
        'Explique a frase "pesquise na web"',
        "Nunca procure na internet",
        "Pesquise não, somente explique a biblioteca",
        "O que é uma célula?",
    ],
)
def test_negation_quotation_or_ordinary_question_never_authorizes_research(message):
    assert not Orchestrator.explicit_research(message)
