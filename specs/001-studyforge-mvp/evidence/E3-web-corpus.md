# Baseline com documentos longos — revisão dos resultados

## Dados e execução

Corpus principal: 12 artigos completos em português, 512.403 caracteres e 65.519 palavras,
com arquivos entre 12.846 e 105.738 caracteres. Os textos sintéticos anteriores estão preservados
em `backend/evals/corpus/synthetic/`. Origem, revisão, autoria, hash e licença dos artigos constam
em `backend/evals/corpus/manifest.json` e `NOTICE.md`.

32 perguntas: 24 sobre seções, 4 combinando documentos e 4 sem resposta no corpus. Há 28 casos
respondíveis. Os rótulos referenciam trechos exatos e offsets verificados por testes.

Embeddings reais: gemini-embedding-001, 768 dimensões, normalizados em L2. Chunking atual:
target 1.600, max 2.400, overlap 200 caracteres, respeitando blocos quando possível. Resultado:
345 chunks. Ranking exato por cosseno no PostgreSQL/pgvector. Template de embedding igual ao da
aplicação: caminho de seção + texto. A biblioteca pessoal não foi alterada.

## Métricas iniciais

Médias por pergunta respondível; não representam percentual de respostas do tutor corretas.

| Medida | top-3 | top-5 | top-8 |
|---|---:|---:|---:|
| Recall dos documentos esperados | 98,21% | 98,21% | 98,21% |
| Cobertura integral das passagens rotuladas | 89,29% | 92,86% | 96,43% |

MRR por documento: 1,0. MRR da primeira passagem rotulada integral: 0,8414.
Perguntas de seção: cobertura das passagens top-5 de 95,83%.
Perguntas que combinam documentos: cobertura top-5 de 75%.

Os quatro casos sem resposta foram excluídos do recall. Seus primeiros resultados tiveram
similaridade aproximadamente 0,517 a 0,571. Isso não estabelece um limiar universal de rejeição;
a existência de um vizinho vetorial não é evidência suficiente para responder.

## Revisão das perdas de cobertura no top-5

- `section-07` (lei de Newton e distância): o rótulo apontava para a introdução do artigo,
  mas o rank 1 recuperou a seção 'Ação à distância newtoniana', com a lei do inverso do quadrado
  e a fórmula. Há suporte equivalente; o zero de cobertura do trecho específico NÃO significa
  falha em encontrar evidência para essa pergunta.
- `multi-03` (algoritmos intermináveis versus falha transacional): foram recuperados os dois
  documentos. A parte transacional veio de 'Façamos uma análise' e 'Sintetizando', incluindo
  a afirmação de que mudanças de uma transação com falha são desfeitas. Há suporte equivalente
  ao rótulo de rollback; outra limitação dos rótulos não exaustivos.
- `multi-02` (respiração nas mitocôndrias e fluxo cíclico): os oito primeiros trechos vieram do
  mesmo artigo Fotossíntese. A passagem esperada do artigo Célula não foi recuperada. É uma
  perda real de diversidade/cobertura entre documentos; aumentar de 5 para 8 não a resolveu.

Os rótulos e o resultado bruto inicial foram preservados, sem alterar os números depois da
inspeção para aparentar melhoria do modelo. Uma rodada futura deve aceitar passagens
alternativas equivalentes e continuar registrando a dificuldade das perguntas compostas.

## Robustez operacional observada

O ensaio encontrou timeout no lote 100; lote 32 sem pausa encontrou 429 e uma retomada pausada
atingiu timeout após 192 vetores. Lote 8 teve uma desconexão remota; a retomada com retry limitado
concluiu os 345 vetores. Queries e trechos já concluídos foram reutilizados do cache exclusivo de
avaliação autorizada. A última etapa levou 130,542 s; esse tempo não inclui toda a preparação,
as falhas anteriores nem os vetores reaproveitados, e NÃO é tempo de ingestão integral do produto.

O cache não recebe conversas ou fontes temporárias da aplicação. Está ignorado por Git e Docker.
As retomadas usaram o mesmo perfil e os mesmos textos, sem misturar dimensões ou tarefas.

## Interpretação

Há um baseline realista inicial de recuperação, mais informativo que os 12 textos sintéticos.
Os números altos por documento escondem diferenças entre recuperar o artigo e cobrir todos os
aspectos da pergunta. O próximo experimento relevante é diversidade/cobertura de perguntas
compostas e refinamento dos julgamentos de relevância, além da comparação de chunking/dimensão.
Nenhuma meta final ou garantia de qualidade foi aprovada por este resultado.

Resultados detalhados: `backend/evals/results/web-768-blocks-1600.json`, com ranking, seções,
linhas, offsets, similaridade e excertos por pergunta. Esses excertos mantêm a licença do corpus.
# Comparação adicional — 2026-10-29

Tentada a configuração de 800 caracteres/768 dimensões: o pipeline produziu 744
trechos. O processo avançou por lotes, mas foi interrompido por 429 do serviço de
embeddings; uma retomada também recebeu 429. Não existe relatório concluído para
essa configuração e nenhum score foi inferido dos lotes incompletos. Cache
autorizado preservado para retomada após disponibilidade da cota. Não executar
novas tentativas em sequência. A dimensão 1536 no corpus longo continua pendente.
