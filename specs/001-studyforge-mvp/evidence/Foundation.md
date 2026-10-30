> Atualização 2026-10-29: referências abaixo ao bloqueio externo G0 são históricas. O usuário limitou a garantia ao armazenamento local e retirou o gate. Resultados de testes anteriores permanecem como executados; integrações reais ainda não foram verificadas.

# Fundação — verificação executada

Data: 2026-10-28. T010–T023 implementadas em contêineres e verificadas com doubles.

- Rodada completa da fundação: **18 passed**, incluindo sessão/epoch/cancelamento,
  budgets/admissão, CSRF/Host/Origin, multipart hostil, política de fornecedor, vetores e logs.
- Rodada adicional de ambiente: **2 passed**, incluindo o teste anterior de pgvector e a
  conexão AsyncSession com a role studyforge_runtime sem privilégios de superusuário.
- Build atualizado passou: TypeScript strict, Vite e imagem Python com locks/hashes.
- Um teste inicial de sanitização estava após o mount estático; corrigido e repetido com sucesso.
- SQLAlchemy recebeu o extra asyncio (greenlet) no lock, necessário para AsyncSession.

Comando da rodada completa:
`docker compose run --rm --no-deps -e TEST_DATABASE_URL=<DSN-local-de-testes> -v <backend>:/workspace/backend:ro app pytest -q -p no:cacheprovider`

Asserções de política usam recibo sintético temporário e cliente falso; não comprovam retenção
do fornecedor. Nenhum recibo real foi fornecido e nenhuma chamada a Gemini/busca foi feita.
G0 permanece BLOQUEADO. A API só poderá enviar conteúdo real após evidência manual compatível,
vinculada ao endpoint/projeto/modelos e validada pelo guard antes da criação do cliente.

Avisos transitivos de depreciação de LangSmith/google-genai permanecem registrados; não houve
erro na suíte aprovada. Tracing e serviços LangSmith continuam desabilitados.
