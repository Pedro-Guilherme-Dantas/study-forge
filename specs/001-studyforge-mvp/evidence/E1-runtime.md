> Atualização 2026-10-29: referências abaixo ao bloqueio externo G0 são históricas. O usuário limitou a garantia ao armazenamento local e retirou o gate. Resultados de testes anteriores permanecem como executados; integrações reais ainda não foram verificadas.

# E1 — bootstrap executado

Data: 2026-10-28. Todos os comandos de ambiente foram executados em contêineres.

- Python 3.14.10; Node 24.22.2 (diferença de patch em relação ao candidato inicial, verificada).
- PostgreSQL 18.6; imagem pgvector 0.8.7-pg18-bookworm com digest fixado no Compose.
- FastAPI 0.162.0, Pydantic 2.14.1, SQLAlchemy 2.1.6, pytest 9.2.0,
  LangChain 1.4.7, LangGraph 1.2.18, langchain-google-genai 4.4.2, google-genai 2.33.0.
- Psycopg 3.3.6 e Alembic 1.20.1; demais versões transitivas constam no requirements.lock.
- React/React DOM 19.3.1, Vite 8.3.5, TypeScript 7.0.2.
- Docker Engine disponível: 28.5.1; Compose disponível: 2.40.3-desktop.1.

Comandos concluídos:

1. Compilação de requirements.lock com uv 0.12.5 em python:3.14-slim; 86 pacotes resolvidos
   com hashes. package-lock.json produzido em Node 24, sem instalar dependências no host.
2. `docker compose build app`: passou, incluindo `tsc --noEmit` e `vite build`.
3. `docker compose run --rm --no-deps app pytest tests/integration/test_environment.py -q
   -p no:cacheprovider`: **1 passed**. Imports da stack e tabela vector real em schema isolado;
   ordenação por cosseno validada. Schema de teste eliminado ao final, sem apagar a biblioteca.

Correções de bootstrap: o primeiro build foi disparado antes de terminar o lock e repetido após
sua geração; TypeScript 7 exigiu a declaração vite/client para o import de CSS. Nenhuma dessas
tentativas foi tratada como validação bem-sucedida.

Avisos: depreciações transitivas em LangSmith/google-genai no Python 3.14; nenhum erro de import.
LangSmith é dependência transitiva de LangChain, mas seu serviço/tracing não foi habilitado.
Fixture loop scope do pytest-asyncio foi explicitado para evitar mudança de default futura.

Limite da evidência: confirma instalação/build/imports/PostgreSQL, não geração Gemini, busca,
retenção externa, semântica de embeddings ou qualidade do produto. G0 continua bloqueado.
