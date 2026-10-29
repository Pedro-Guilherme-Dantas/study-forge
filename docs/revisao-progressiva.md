# Revisão progressiva da implementação

Iniciada em 29/10/2026 por solicitação do usuário, depois de criar o guia didático.

## Método e limites

Esta sequência reconstrói etapas lógicas da implementação existente. Não recria
datas ou commits antigos e não reescreve o commit inicial. Cada área é inspecionada,
seus testes relevantes são executados em contêiner e seus arquivos são adicionados
explicitamente ao Git. Segredos, caches e artefatos de dependências ficam excluídos.

As verificações durante a revisão usam o diretório de trabalho integrado. Como os
arquivos atuais têm dependências entre áreas, os commits intermediários não são
apresentados como releases isoladas já executáveis. A revisão final deve verificar
o conjunto versionado completo. Nenhum push é necessário para organizar o histórico.

## Etapas

| Etapa | Escopo | Situação e evidência |
|---|---|---|
| 0 | Guia de arquitetura e fluxos | Criado e revisado contra o código; commit d25523f. |
| 1 | Constituição, especificação e contratos | Revisados princípios, escopo, retenção e consentimento. Corrigidas referências remanescentes ao gate externo já retirado. |
| 2 | Contêineres, dependências, modelos e migrações | Build/typecheck e 3 testes aprovados. Inclui upgrade → downgrade → upgrade em schema isolado. Regex declarado como dependência direta na versão já travada. |
| 3 | Pipeline textual, biblioteca e publicação | Pendente nesta revisão. |
| 4 | Recuperação, tutor, pesquisa e provedores | Pendente nesta revisão. |
| 5 | Seleção, API, sessão e proteção dos fluxos | Pendente nesta revisão. |
| 6 | Interface e cliente HTTP | Pendente nesta revisão. |
| 7 | Avaliações, evidências e verificação integrada | Pendente nesta revisão. |

Tarefas ainda abertas em tasks.md não serão encerradas por criar um commit.
Falhas, correções e limites encontrados na revisão devem ser acrescentados aqui.

## Organização das pastas — revisão incremental

- **Documentação:** docs/ explica; specs/ contém requisitos, contratos e evidências;
  .specify/ e .agents/ contêm ferramentas do fluxo de desenvolvimento. Separação adequada.
- **Infraestrutura e dados:** Compose na raiz, Dockerfiles junto de cada aplicação,
  migrações fora de app/db/ e contratos fora do código. Adequado ao monólito e sem
  serviços extras. Manifests/locks pertencem a seus runtimes; regex não depende
  mais acidentalmente de uma dependência transitiva.
- .env, caches, node_modules, dist e bytecode foram verificados como ignorados.
- A validação de migrações inicializa alembic_version no schema de ensaio para não
  confundir a biblioteca pública já migrada com um schema vazio pelo search_path.
