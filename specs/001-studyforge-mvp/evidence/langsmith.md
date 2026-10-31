# Integração opcional LangSmith — 2026-10-29

Solicitada pelo usuário para diagnóstico e apresentação do harness. Captura somente metadados
operacionais; não altera retenção local ou autoridade dos agentes. SDK 0.14.14 já presente no
lock, agora declarado como dependência direta. Sem novos serviços ou bancos.

## Resultados executados em containers

- Testes iniciais de política/tracing: **14 passed**.
- Ensaio offline com grafo/orquestrador reais e recuperação/tutor de fixture: recuperação,
  insuficiência, recusa, falha simulada e pesquisa explícita; sem Gemini/Brave ou escrita na biblioteca.
- Suíte completa com schemas PostgreSQL isolados e contrato atualizado:
  **136 passed, 2 skipped, 18 warnings, 13,61 s**. Skips são testes externos Gemini/web opt-in;
  warnings são depreciações transitivas. Testes cobrem privacidade, isolamento, hierarquia,
  filas limitadas, indisponibilidade do exportador e divulgação/status protegido.
- `docker compose build --quiet app`: concluído, incluindo typecheck e build frontend.
- Ensaio remoto com chave do `.env`: **5 árvores aceitas, 0 falhas, 0 descartes**.
  Consulta posterior confirmou **5 roots indexados**, todos com entradas vazias e metadata
  de fixture. Falha simulada mostra `EXTERNAL_UNAVAILABLE`; pesquisa explícita terminou como
  `partial`, esperado para o tutor extrativo de fixture.
- Aplicação recriada com tracing habilitado; readiness **HTTP 200**. Status confirmou
  `enabled=true`; divulgação na interface menciona envio ao LangSmith.
- `git diff --check`: sem erros de whitespace. Sem `git add` ou commit nesta integração.

## Limites

O ensaio confirma exportação e indexação via API, não revisão visual do painel. Fixtures
exercitam o harness, não a qualidade semântica do Gemini ou acesso real ao Brave.
Não há métricas automáticas de tokens/custo nem captura de conteúdo. Conferir sustentação
pela interface e avaliações separadas. Fila RAM de oito árvores, até 64 spans por árvore,
dez segundos por exportação e uma tentativa HTTP; sem spool/replay em disco.
Falha intermediária pode deixar árvore remota parcial; desligamento descarta fila pendente.
Contadores do processo principal não incluem o ensaio executado em outro container.
Credenciais não foram exibidas. As pendências anteriores do MVP permanecem abertas.

Guia e roteiro: `docs/observabilidade-langsmith.md`. Ensaio: `python -m evals.trace_demo`.
