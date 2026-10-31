# Comparação de embeddings: Gemini e E5-small local

Data: 29/10/2026.

**Resultado:** o E5-small foi viável nesta máquina em memória e tempo de execução, mas perdeu qualidade de recuperação na configuração testada. Não recomendo substituir diretamente o Gemini por ele. A configuração da aplicação permanece inalterada.

## Como foi feita

- Corpus: 12 artigos públicos em português, aproximadamente 512 mil caracteres. Foram usadas as mesmas 32 perguntas da avaliação existente: 28 com evidência e quatro sem resposta no corpus.
- Referência: resultado salvo do `gemini-embedding-001`, com 768 dimensões. Não fiz novas chamadas ao Gemini nesta comparação.
- Candidato: `intfloat/multilingual-e5-small`, revisão `614241f622f53c4eeff9890bdc4f31cfecc418b3`, ONNX FP32, 384 dimensões. Foram aplicados os prefixos `query:` e `passage:`, média ponderada pela máscara de atenção e normalização L2, conforme a orientação do modelo.
- Execução: container, CPU, quatro threads, lotes de oito e limite de 3 GiB. Máquina com Ryzen 5 5500 e 16 GB de RAM; a GPU não foi usada.
- Recuperação: distância de cosseno exata no pgvector, em tabela temporária. Os hashes do corpus, os trechos e a configuração do processamento foram conferidos contra a referência.

Fiz duas execuções completas, sem reutilizar embeddings locais. Os resultados agregados de recuperação foram idênticos entre elas. Também verifiquei a equivalência entre processamento individual e em lote, além da preservação do conteúdo na subdivisão dos trechos.

## Qualidade de recuperação

O indicador principal abaixo mede a cobertura das evidências esperadas entre os cinco primeiros trechos, com média por pergunta. Encontrar o documento correto, sozinho, não garante encontrar a passagem necessária.

| Configuração | Trechos | Documento correto @5 | Evidências recuperadas @5 | Evidências recuperadas @8 |
|---|---:|---:|---:|---:|
| Gemini, referência salva | 345 | 98,21% | **92,86%** | 96,43% |
| E5-small, mesmos trechos | 345 | 89,29% | **75,00%** | 82,14% |
| E5-small, subdivisão para caber em 512 tokens | 410 | 94,64% | **67,86%** | 78,57% |

Dos 345 trechos originais, 65 ultrapassaram o limite de 512 tokens do E5 e foram truncados na primeira variante. Na segunda, subdividi esses trechos sem perder texto ou localização de origem. Isso melhorou a seleção dos documentos, mas piorou a cobertura das evidências com o mesmo número de resultados: mais fragmentos passaram a competir pelas cinco posições.

A perda da primeira variante foi de **17,86 pontos percentuais** em evidências @5. Nas quatro perguntas que combinam documentos, nenhuma das passagens de referência apareceu no top 5 do E5. A inspeção dos resultados mostrou problemas concretos: por exemplo, uma pergunta sobre média ponderada e divisão de frações retornou apenas fragmentos de frações, sem a evidência sobre média.

## Tempo e memória observados

| Medida | E5-small local, duas execuções |
|---|---:|
| Carregar modelo e tokenizer | 3,1–4,0 s |
| Primeira pergunta após carregar | 17–20 ms |
| Embedding de pergunta, mediana com modelo carregado | 7,1–7,8 ms |
| Embedding de pergunta, percentil 95 | aproximadamente 16 ms |
| Gerar embeddings dos 345 trechos | 51,6–52,2 s |
| Gerar embeddings dos 410 trechos | 61,6–61,9 s |
| Pico de memória do processo de avaliação | aproximadamente 1,4 GiB |

Esses tempos de pergunta medem **somente a geração do embedding**, não a resposta completa do tutor. Foram 64 medições de perguntas por execução. O carregamento foi medido em processos novos, mas com os arquivos já disponíveis no cache do sistema.

O download inicial dos pesos levou aproximadamente 196 s e não entra no tempo de inferência. A duração salva da avaliação Gemini corresponde a uma execução retomada com cache; portanto, não permite uma comparação justa de velocidade entre API e modelo local.

## Limitações e decisão prática

Este é um corpus pequeno, com textos em português, fórmulas e ruído de extração. As marcações de evidência não são exaustivas. As quatro perguntas sem resposta foram excluídas das métricas de recuperação; não avaliei aqui a geração de respostas nem o reconhecimento de ausência de evidência pelo tutor.

O teste mostra que **um modelo local desse porte cabe nesta máquina e responde rapidamente**, mas não que qualquer modelo local terá essa qualidade. Antes de migrar, vale experimentar um modelo local mais forte ou ajustar recuperação e segmentação, repetindo a mesma avaliação. A subdivisão simples, isoladamente, não resolveu o problema.

## Artefatos

- Implementação do experimento: `backend/evals/local_cpu/`.
- Execuções: `backend/evals/results/local-e5-small-comparison-run1.json` e `local-e5-small-comparison.json`.
- Verificações: `backend/evals/results/local-e5-small-verification.json`.
- Referência Gemini: `backend/evals/results/web-768-blocks-1600.json`.
- Instruções do modelo: [model card oficial](https://huggingface.co/intfloat/multilingual-e5-small).

Os artefatos foram inicialmente mantidos fora do stage conforme solicitado. A revisão
de 31/10/2026 os organiza para versionamento; pesos e caches continuam ignorados.
Comandos de reprodução: [README do experimento](../backend/evals/local_cpu/README.md).
