# E3 — recuperação com embeddings reais

## Corpus sintético inicial — histórico, insuficiente para avaliar textos longos

Foram executadas consultas reais a gemini-embedding-001, dimensões 768 e 1.536, com PostgreSQL/pgvector.
O corpus original tinha 12 textos curtos e 12 perguntas; ambas as configurações de chunking
produziam os mesmos 12 trechos. Nos 11 casos respondíveis, Recall@3/5/8 e MRR foram 1,0.
Consultas repetidas tiveram cosseno mínimo aproximadamente 1,0 nessa amostra.

Esse resultado NÃO demonstra qualidade em documentos extensos e NÃO justifica um top-k ou
chunking definitivo. O usuário identificou essa limitação e pediu materiais reais da web.
Os arquivos originais foram preservados em `backend/evals/corpus/synthetic/`.

## Corpus web selecionado para avaliação pelo usuário

12 artigos completos da Wikipédia em português, 512.403 caracteres e 65.519 palavras no total.
Arquivos de 12.846 a 105.738 caracteres. Origem, revisão, autoria, licença CC BY-SA 4.0,
instante de obtenção e hash estão no manifesto. Texto extraído da API e convertido para Markdown
sem resumo; equações podem manter representações textuais/LaTeX da fonte. Isso também introduz
ruído de formatação, relevante ao interpretar os resultados. Não foi feita validação científica
do conteúdo dos artigos.

32 perguntas propostas: 24 de seções, 4 de combinação entre documentos e 4 sem resposta no corpus.
Os rótulos têm trechos exatos e offsets verificáveis. São julgamentos iniciais, não exaustivos;
outra passagem pode sustentar uma resposta mesmo sem corresponder ao trecho originalmente rotulado.

O runner usa o mesmo normalizador/chunker e template de embedding da ingestão da aplicação,
normalização L2, busca exata por cosseno no pgvector e desempate estável. Além de recall/MRR por
documento, calcula cobertura dos trechos esperados em top-3/5/8. Casos sem resposta não entram
no denominador do recall; semelhança vetorial não prova que exista evidência para responder.

## Falhas observadas antes de obter um baseline longo

- Lote de 100 trechos: timeout de leitura, sem métrica válida de recuperação.
- Lote de 32 sem espaçamento: HTTP 429, sem métrica válida de recuperação.
- Revisão: lote de 32, pausas de 20 segundos e respeito a RetryInfo dentro do orçamento.
  Embeddings parciais concluídos são mantidos somente em cache de avaliação do corpus explicitamente
  autorizado, separado do produto, ignorado por Git e pelo build. Conversas/fontes temporárias
  da aplicação não usam esse cache.

Baseline longo em execução; resultados completos serão registrados após a conclusão, sem
transformar falha de processamento em índice de relevância ou presumir os resultados do corpus curto.

## Baseline longo concluído

O baseline de 768 dimensões foi concluído com 345 trechos. Recall de documentos top-5: 98,21%; cobertura das passagens rotuladas top-5: 92,86%. Revisão manual identificou dois casos com passagens equivalentes ao rótulo e um caso real de perda de cobertura entre documentos. Métricas, falhas, metodologia e limitações em [E3-web-corpus.md](E3-web-corpus.md). Comparações longas com 1.536 dimensões/chunking 800 ainda não foram executadas. Não confundir a conclusão deste baseline com fechamento de toda T049.
