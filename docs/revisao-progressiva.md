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
| 3 | Pipeline textual, biblioteca e publicação | 33 testes aprovados em 4,25 s; rastreabilidade, Unicode, publicação atômica, retry, limites e regressões dos consumidores. Helper de biblioteca centralizado em tests/support.py. |
| 4 | Recuperação, tutor, pesquisa e provedores | 67 testes aprovados em 4,13 s; papéis, consentimento, schema/citações, retentativas, SSRF e recuperação por perfil/versão. Sem chamadas externas nesta revisão. |
| 5 | Seleção, API, sessão e proteção dos fluxos | 30 testes aprovados em 5,83 s. Corrigida seleção repetida com executor cheio: apenas trabalho novo reserva capacidade. Regressão reproduziu 429 antes da correção e passou depois. |
| 6 | Interface e cliente HTTP | Build/typecheck e 6 testes do cliente aprovados. Corrigidas respostas tardias após reset/fechamento e reativação de sessão antiga; não há replay automático. Removido fallback de navegação inalcançável. |
| 7 | Avaliações, evidências e verificação integrada | Pendente nesta revisão. |

Tarefas ainda abertas em tasks.md não serão encerradas por criar um commit.
Falhas, correções e limites encontrados na revisão devem ser acrescentados aqui.

## Organização das pastas — revisão incremental

- **Documentação:** docs/ explica; specs/ contém requisitos, contratos e evidências;
  .specify/ e .agents/ contêm ferramentas do fluxo de desenvolvimento. Separação adequada.
  A configuração instalada do Spec Kit/Git foi preservada; auto-commit continua
  desativado. Os commits desta revisão usam seleção explícita, sem executar hooks
  que adicionariam todas as alterações automaticamente. .gitattributes fixa LF
  para fontes/textos e mantém capturas binárias sem conversão.
- **Infraestrutura e dados:** Compose na raiz, Dockerfiles junto de cada aplicação,
  migrações fora de app/db/ e contratos fora do código. Adequado ao monólito e sem
  serviços extras. Manifests/locks pertencem a seus runtimes; regex não depende
  mais acidentalmente de uma dependência transitiva.
- .env, caches, node_modules, dist e bytecode foram verificados como ignorados.
- A validação de migrações inicializa alembic_version no schema de ensaio para não
  confundir a biblioteca pública já migrada com um schema vazio pelo search_path.
- **Pipeline:** ingestion/ separa validação, normalização, chunking, extração,
  serviço de publicação e promoção. A separação é proporcional; não há necessidade
  demonstrada de criar pacotes ou serviços adicionais. Modelos permanecem em db/,
  sem misturar transformação textual e controle de sessão.
- **Testes:** preparação compartilhada de biblioteca foi extraída para
  tests/support.py, eliminando importação de test_ingestion_publication para obter
  um helper. Fixtures continuam em tests/fixtures/, separadas do corpus de avaliação.
- **Agentes e integrações:** agents/ organiza os papéis e o grafo; providers/
  encapsula os SDKs. retrieval.py e citations.py são serviços pequenos compartilhados,
  sem justificar camadas adicionais. web_fetch.py é a fronteira específica de rede
  não confiável; mantê-la explícita é preferível a escondê-la dentro de um agente.
  Nenhum desses módulos expõe uma ferramenta de persistência ao modelo.
- **API e ciclo de vida:** api/ contém adaptação HTTP; promoção, estado de sessão,
  orçamento e persistência continuam em serviços próprios. main.py funciona como
  montagem das dependências. Estrutura adequada para um processo; não introduzir
  repositories/interfaces genéricos sem uma necessidade concreta.
- Preparação de sessão/pesquisa e helpers HTTP também foram centralizados em
  tests/support.py. A busca por imports entre tests.contract/test_* e
  tests.integration/test_* não encontrou mais dependência desse tipo.
- **Frontend:** pages/ organiza os quatro destinos; components/ guarda elementos
  reutilizados e responsabilidades como Markdown seguro, citações e modal. api.ts
  concentra sessão/transporte e types.ts define contratos. Estrutura adequada sem
  criar store global ou camada extra. O CSS centralizado é aceitável neste MVP;
  só deve ser dividido quando os estilos passarem a dificultar mudanças concretas.

## Correções reproduzidas

1. Seleção repetida com executor cheio retornava 429. Teste falhou antes da mudança;
   agora reaproveita o recibo sem reservar capacidade e continua recusando trabalho novo.
2. Resposta antiga de criação de sessão podia substituir uma sessão nova após reset.
   Teste do cliente reproduziu a aceitação indevida; geração de contexto impede isso.
   Respostas de fonte atrasadas também são recusadas após reset ou fechamento,
   preservando a sessão válida quando apenas a conversa foi encerrada.
3. Manifesto não declarava regex como dependência direta, apesar de importar a
   biblioteca. Mantida a versão exata já presente no lock, sem trocar modelos/SDKs.
