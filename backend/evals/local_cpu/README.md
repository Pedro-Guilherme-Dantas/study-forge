# Experimento CPU de embeddings

Código de avaliação isolado; não altera o provedor da aplicação. Resultados e
limitações: `docs/comparacao-embeddings-locais.md`. Pesos e entradas ficam no cache
ignorado; os JSONs de resultados usam somente o corpus público de avaliação.

Preparação em PowerShell na raiz do repositório (Docker em execução):

```powershell
docker compose up -d db
docker compose build app
docker compose run --rm --no-deps --user root -v "${PWD}/backend/evals/.cache:/workspace/backend/evals/.cache" app python -m evals.local_cpu.prepare
docker build -f backend/evals/local_cpu/Dockerfile -t studyforge-local-eval .
New-Item -ItemType Directory -Force backend/evals/.cache/local-models, backend/evals/.cache/local-results | Out-Null
docker run --rm --memory=3g --cpus=4 --network studyforge_default -e EVAL_DATABASE_URL=postgresql://studyforge:studyforge-local@db:5432/studyforge -v "${PWD}/backend/evals/.cache/local-comparison:/data" -v "${PWD}/backend/evals/.cache/local-models:/models" -v "${PWD}/backend/evals/.cache/local-results:/results" studyforge-local-eval
```

A primeira execução baixa artefatos públicos fixados por revisão do E5, sem
executar código remoto. Resultados novos ficam em `.cache/local-results`, sem
sobrescrever os resultados históricos versionados. A consulta usa tabela SQL
temporária e não altera a biblioteca. A credencial acima é a credencial local do
Compose, usada para o experimento, não uma chave externa.

Para repetir e verificar, preserve o primeiro resultado como
`local-e5-small-comparison-run1.json` no mesmo diretório de saída, execute novamente
o `docker run` e depois repita-o acrescentando `python verify.py`. Esse último
comando verifica equivalência de métricas, lotes/padding e cobertura da subdivisão.
Os comandos são instruções de reprodução, não um registro de execução desta revisão.
