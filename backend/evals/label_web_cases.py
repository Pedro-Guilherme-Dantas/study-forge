"""Human-readable proposed relevance labels anchored to exact imported source passages."""

import json
from pathlib import Path

ROOT = Path(__file__).parent
SINGLE = [
    (
        "celula",
        "Qual estrutura organiza fibras, mantém a forma celular e participa da endocitose?",
        "O citoesqueleto é uma rede de fibras",
    ),
    (
        "celula",
        "Qual a diferença entre o núcleo de células procarióticas e eucarióticas?",
        "As células procarióticas não possuem o núcleo delimitado por membrana",
    ),
    (
        "fotossintese",
        "Como funciona o retorno de elétrons no transporte cíclico que envolve apenas o fotossistema I?",
        "os elétrons da ferredoxina voltam ao complexo citocromo b6f",
    ),
    (
        "fotossintese",
        "Que experimento com isótopos esclareceu a origem do oxigênio liberado durante a fotossíntese?",
        "Experimentos com água marcada por oxigênio-18 confirmaram que o O2 da fotossíntese vem da água",
    ),
    (
        "mitose",
        "Em qual etapa os cromossomos condensados se alinham no centro da célula e formam uma placa equatorial?",
        "os cromossomos condensados alinham-se no centro da célula",
    ),
    (
        "mitose",
        "O que acontece com cromátides-irmãs quando são puxadas para polos opostos?",
        "separam-se e deslocam-se para pólos opostos da célula",
    ),
    (
        "gravidade",
        "Como a atração entre duas massas pontuais varia com a distância na descrição de Newton?",
        "inversamente proporcional ao quadrado da distância entre elas",
    ),
    (
        "gravidade",
        "Como um objeto massivo pode produzir várias imagens de um quasar distante?",
        "um objeto com massa suficiente pode desviar a luz ao seu redor e produzir uma lente gravitacional",
    ),
    (
        "inercia",
        "O que acontece com a velocidade de um corpo sem força resultante num referencial inercial?",
        "um corpo sobre o qual a força resultante é nula mantém uma velocidade vetorial constante",
    ),
    (
        "inercia",
        "Como a teoria do ímpeto foi restringida ao movimento linear antes de Galileu?",
        "Giambattista Benedetti modificou a crescente teoria do ímpeto para restringi-la ao movimento linear",
    ),
    (
        "energia",
        "Como o teorema de Noether relaciona energia conservada e simetria temporal?",
        "se essa simetria tem independência temporal, então a quantidade conservada é chamada de",
    ),
    (
        "energia",
        "Que condição sobre o sistema permite dizer que sua energia total permanece constante?",
        "a quantidade total de energia em um sistema isolado permanece constante",
    ),
    (
        "fracao",
        "Como transformar uma divisão de frações em uma multiplicação?",
        "multiplica-se a fração que está no numerador pelo inverso da fração que está no denominador",
    ),
    (
        "fracao",
        "Depois de calcular o MMC, como se obtém o novo numerador de uma fração?",
        "dividimos o número",
    ),
    (
        "primo",
        "Quem demonstrou que existem infinitos números primos e aproximadamente quando?",
        "Há infinitos números primos, como demonstrado por Euclides por volta de 300 a.C.",
    ),
    (
        "primo",
        "Qual método grego ainda é usado para construir listas de números primos?",
        "o crivo de Eratóstenes, ainda é utilizado para construir listas de primos",
    ),
    (
        "media",
        "Como calcular uma média quando cada observação recebe um peso diferente?",
        "A média aritmética ponderada desses n números é a soma dos produtos",
    ),
    (
        "media",
        "Qual foi a média do exemplo com nota 10 no teste de peso 1 e nota 4 na prova de peso 2?",
        "o resultado da média aritmética ponderada para este exemplo é 6",
    ),
    (
        "algoritmo",
        "Por que não é possível decidir o sucesso de todo algoritmo apenas interpretando sua resposta?",
        "Para algoritmos intermináveis o sucesso não pode ser determinado pela interpretação da resposta",
    ),
    (
        "algoritmo",
        "Por que duas sequências de instruções podem exigir tempos, espaços ou esforços diferentes?",
        "Tal diferença pode ser reflexo da complexidade computacional aplicada",
    ),
    (
        "transacao",
        "O que deve acontecer com toda a transação se uma ação da unidade de trabalho falhar?",
        "a transação inteira deve ser desfeita (rollback)",
    ),
    (
        "transacao",
        "Qual propriedade mantém os resultados de uma transação mesmo depois de uma falha posterior?",
        "Essa propriedade é conhecida como durabilidade",
    ),
    (
        "evidencia",
        "Quais formas de contestação podem ser aplicadas a uma afirmação científica?",
        "Uma afirmação de verdade científica pode ser contestada pela refutação",
    ),
    (
        "evidencia",
        "Que tipos de testes podem ser escolhidos para avaliar uma hipótese e suas previsões?",
        "que podem incluir experimentos de laboratório ou estudos duplo-cego",
    ),
]
MULTI = [
    (
        "Compare a participação do citoesqueleto na citocinese com a separação celular descrita na mitose.",
        [
            ("celula", "Também atua durante a endocitose"),
            ("mitose", "No final da Telófase inicia-se o processo de Citocinese"),
        ],
    ),
    (
        "Relacione a respiração nas mitocôndrias com o fluxo cíclico de elétrons usado para ajustar a produção de ATP.",
        [
            ("celula", "A respiração ocorre nas mitocôndrias celulares"),
            (
                "fotossintese",
                "No transporte cíclico, que envolve apenas o fotossistema I",
            ),
        ],
    ),
    (
        "Compare a impossibilidade de determinar o sucesso de algoritmos intermináveis com o tratamento de falhas de uma unidade de trabalho transacional.",
        [
            (
                "algoritmo",
                "Para algoritmos intermináveis o sucesso não pode ser determinado",
            ),
            ("transacao", "a transação inteira deve ser desfeita (rollback)"),
        ],
    ),
    (
        "Como se faz uma média com pesos diferentes e como a divisão de frações pode ser reescrita como multiplicação?",
        [
            (
                "media",
                "A média aritmética ponderada desses n números é a soma dos produtos",
            ),
            ("fracao", "multiplica-se a fração que está no numerador pelo inverso"),
        ],
    ),
]
NEGATIVE = [
    "Qual é a capital da Islândia?",
    "Qual é o número de série do notebook do usuário?",
    "Qual a dose recomendada de um medicamento específico para meu diagnóstico?",
    "Qual foi a temperatura exata registrada nesta sala ontem às 14h?",
]


def label(document, anchor):
    body = (ROOT / "corpus" / (document + ".md")).read_text(encoding="utf-8")
    start = body.find(anchor)
    if start < 0:
        raise ValueError(f"Unmatched label in {document}: {anchor}")
    headings = []
    for line in body[:start].splitlines():
        if line.startswith("#"):
            depth = len(line) - len(line.lstrip("#"))
            headings = headings[: depth - 1] + [line.lstrip("# ")]
    return {
        "document_id": document,
        "quote": anchor,
        "start_char": start,
        "end_char": start + len(anchor),
        "section_path": headings,
        "start_line": body.count("\n", 0, start) + 1,
    }


def main():
    cases = []
    for index, (document, question, anchor) in enumerate(SINGLE, 1):
        cases.append(
            {
                "id": f"section-{index:02}",
                "kind": "section",
                "question": question,
                "relevant_documents": [document],
                "unanswerable": False,
                "evidence": [label(document, anchor)],
            }
        )
    for index, (question, anchors) in enumerate(MULTI, 1):
        cases.append(
            {
                "id": f"multi-{index:02}",
                "kind": "cross_document",
                "question": question,
                "relevant_documents": [d for d, _ in anchors],
                "unanswerable": False,
                "evidence": [label(d, a) for d, a in anchors],
            }
        )
    for index, question in enumerate(NEGATIVE, 1):
        cases.append(
            {
                "id": f"absent-{index:02}",
                "kind": "unanswerable",
                "question": question,
                "relevant_documents": [],
                "unanswerable": True,
                "evidence": [],
            }
        )
    (ROOT / "retrieval_cases.jsonl").write_text(
        "\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "cases": len(cases),
                "section": len(SINGLE),
                "cross_document": len(MULTI),
                "unanswerable": len(NEGATIVE),
            }
        )
    )


if __name__ == "__main__":
    main()
