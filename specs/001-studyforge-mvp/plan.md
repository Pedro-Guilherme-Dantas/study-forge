# Implementation Plan: StudyForge — MVP

**Branch**: `001-studyforge-mvp` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Input**: Constituição v1.0.0, especificação revisada, cinco respostas da clarificação e stack
fornecida pelo usuário. Acesso exclusivo nesta máquina, via localhost, confirmado durante o
planejamento. Este é um desenho revisável; não representa implementação ou integração executada.

## Summary

Entregar biblioteca Markdown, tutor com RAG e citações consultáveis, pesquisa HTML temporária,
seleção explícita para guardar fontes e progresso operacional. Preservar integralmente:

- Pedido explícito inicia pesquisa sem nova confirmação. Insuficiência ou incompletude
  considerável da base gera uma oferta; somente aceitar a oferta inicia pesquisa. Recusar fecha
  a oferta e retorna à interface normal sem buscar, extrair ou executar o fluxo.
- Fontes não selecionadas duram até encerrar explicitamente a conversa ou reiniciar a aplicação,
  o que ocorrer primeiro. Navegar entre telas não encerra a conversa.
- Todo histórico fica apenas em memória. Encerrar a conversa descarta mensagens, referências,
  contexto e fontes não selecionadas, abrindo chat vazio. Reinício não restaura conversas.
- Biblioteca e fontes já guardadas permanecem persistidas. Nenhum agente autoriza gravação.
- Progresso mostra estados de materiais, pesquisas e ingestões; não mede aprendizado.

**Desenho recomendado**: monólito modular FastAPI, um processo/worker, tarefas assíncronas
limitadas no mesmo processo e PostgreSQL/pgvector. React é servido pelo próprio backend no
perfil de demonstração. Compose tem dois serviços de execução, `app` e `db`; Node/Vite entram
no build e no perfil de desenvolvimento. Sem Redis, broker, segundo banco ou serviço de agentes.

**Retenção revisada em 2026-10-29**: a garantia de descarte vale para o armazenamento local do StudyForge. O usuário retirou o gate externo G0: APIs de IA e busca seguem as políticas de seus provedores, sem exigência de retenção zero ou comprovante. A interface informa o envio externo. Credenciais/configuração e validação das integrações continuam necessárias; seleção explícita continua obrigatória para a biblioteca.

## Technical Context

**Language/Version**: TypeScript e Python. Candidatos de experimento: TypeScript 7.0.2,
Node 24.22.1 LTS e Python 3.14.10. Resolver compatibilidade em E1 antes de gerar locks definitivos.

**Primary Dependencies**: React/React DOM 19.3.1, Vite 8.3.5, CSS puro; FastAPI 0.162.0,
Pydantic 2.14.1, SQLAlchemy 2.1.6; LangGraph 1.2.18, LangChain 1.4.7,
langchain-google-genai 4.4.2, google-genai 2.33.0. Valores são candidatos documentais,
não conjunto já instalado/testado. Psycopg 3 e Alembic são propostas pequenas de driver/migração.
Versões e evidências em [research.md](research.md#r1-versões-candidatas-e-compatibilidade).

**Storage**: PostgreSQL 18.6 como candidato; imagem documentada
`pgvector/pgvector:0.8.7-pg18-bookworm`, com versão interna e digest a conferir em E1.
Extensão pgvector 0.8.7, biblioteca Python pgvector 0.5.1. Apenas conteúdo local enviado ou web
selecionado vai ao banco. Conversas, pesquisa, ofertas e citações temporárias ficam na RAM.

**Testing**: pytest para unidade, contratos HTTP, PostgreSQL real, agentes com doubles e integrações
externas opt-in; compilação TypeScript separada do build Vite; ensaio de UI com roteiro verificável.
Automação de navegador via pytest/Playwright pode ser acrescentada se o ensaio manual não bastar
para cobrir os caminhos críticos, sem torná-la uma nova plataforma do produto.

**Target Platform**: navegador nesta máquina, backend/DB em contêineres Linux. Publicar somente
`127.0.0.1:8000`; não publicar a porta PostgreSQL. Desenvolvimento Vite opcional em loopback.
Não há exposição pública ou em LAN. Sem cadastro/login de usuários no desenho inicial;
cookie efêmero identifica a sessão local, sem constituir um sistema multiusuário.

**Project Type**: aplicação web pessoal com um backend modular.

**Performance Goals**: medir latência de cada etapa e duração das jornadas. Metas finais abertas.
As propostas anteriores de 2 s/30 s e percentuais da especificação não viraram compromissos.
Usar limites finitos de laboratório em E1–E6 e recalibrar com os resultados.

**Constraints**: HTML/Markdown; nenhuma gravação de conteúdo não selecionado; autorização fora
dos agentes; execução limitada; não publicar documentos parcialmente ingeridos. LangSmith não
é necessário e ficará desabilitado para conteúdo do usuário.

**Scale/Scope**: uma pessoa, uma instância, um worker, uma conversa ativa por sessão local.
Os limites de laboratório recusam excesso com mensagem explícita; não expiram fontes silenciosamente.
Amostras e parâmetros iniciais são hipóteses de teste, não garantias de capacidade.

**Container Environment**: Docker Compose existente no host; instalação, build, testes e
experimentos dentro dos contêineres. Imagens com patch/digest, dependências com locks e hashes
após E1. Apenas PostgreSQL recebe volume durável; `app` não recebe volume de conteúdo, logs
ou checkpoints. Desabilitar core dumps, logs de corpo e swap/paginação de memória temporária no
ambiente de execução quando necessário à garantia; a validação E0 também cobre Docker Desktop/VM.
Não prometer apagamento físico seguro da RAM por um coletor de lixo Python.

## Constitution Check

Avaliação antes da pesquisa e reavaliação após o desenho:

| Princípio | Antes da pesquisa | Após o desenho / evidência |
|-----------|-------------------|----------------------------|
| I. Evidências e origem | PASS no escopo | PASS de desenho: locators, snapshots e validador de citações; E3/E6 e contratos. |
| II. Conteúdo sem autoridade | PASS como obrigação | PASS de desenho: ferramentas limitadas, saídas tipadas, permissões na aplicação; teste hostil E6. |
| III. Controle de persistência | Verificar armazenamento local | Garantia local: separação RAM/SQL e seleção atômica; envio externo informado, sem gate de retenção zero. |
| IV. Regras determinísticas | PASS como obrigação | PASS de desenho: pipeline versionado e promoção externa ao grafo; data-model.md. |
| V. Simplicidade | PASS | PASS de desenho: monólito, um banco, sem fila distribuída; diagnóstico mínimo. |
| VI. Qualidade observável | PASS como obrigação | PASS de desenho: matriz FR/US, testes determinísticos, retrieval e agentes separados. Resultados reais pendentes. |
| VII. Limites e falhas | Exigir orçamento finito | PASS de desenho: deadlines, semáforos, retries limitados e publicação transacional; E4/E5/E6. |
| VIII. Contêineres | PASS | PASS de desenho: Compose, locks após E1 e roteiro sem dependências instaladas no host. |

**Resultado**: desenho completo para revisão e tarefas de experimentação. Resultados com
fixtures e resultados de serviços reais devem ser registrados separadamente; testes sem
credenciais não comprovam integração externa. O gate de retenção zero externa foi retirado
pelo usuário. Integrações reais exigem configuração, limites e os controles locais previstos.

## Project Structure

### Documentation (this feature)

```text
specs/001-studyforge-mvp/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api.md
│   ├── openapi.json
│   └── agents.md
└── checklists/requirements.md
```

`tasks.md` será produzido por `/speckit-tasks`, não neste comando.

### Source Code (repository root)

Estrutura proposta, ainda sem implementação:

```text
compose.yaml
.env.example
frontend/
├── Dockerfile
├── package.json
├── package-lock.json
├── vite.config.ts
└── src/
    ├── App.tsx
    ├── api.ts
    ├── types.ts
    ├── styles.css
    ├── components/       # Citation, StatusBadge, ErrorNotice, MarkdownView
    └── pages/            # Chat, Library, Progress, Sources
backend/
├── Dockerfile           # build Node + runtime Python no perfil demo
├── pyproject.toml
├── requirements.lock
├── migrations/          # Alembic: esquema autorizado e versão vetorial
├── app/
│   ├── main.py
│   ├── settings.py      # configuração Pydantic; segredos só no backend
│   ├── schemas.py       # contratos HTTP e referências discriminadas
│   ├── api/             # sessions, chat, research, sources, materials, operations
│   ├── agents/          # graph.py, orchestrator.py, researcher.py, tutor.py
│   ├── ingestion/       # validate.py, normalize.py, chunk.py, service.py
│   ├── retrieval.py     # SQL pronto + ranking temporário, sem gravação
│   ├── providers/       # gemini.py, search.py; só fronteiras externas necessárias
│   ├── web_fetch.py     # obtenção segura e extração sem acesso ao banco
│   ├── sessions.py      # memória, locks, epochs e descarte de conversa
│   ├── operations.py    # executor limitado no processo; transições explícitas
│   └── db/             # models.py, session.py, consultas explícitas
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   └── fixtures/        # somente materiais sintéticos/autorizados
└── evals/
    ├── corpus/
    ├── retrieval_cases.jsonl
    ├── agent_cases.jsonl
    └── run.py
```

**Structure Decision**: módulos por responsabilidade, funções curtas e contratos Pydantic nos
limites. SQLAlchemy usado diretamente por serviços de aplicação; sem repository genérico,
framework de plugins, heranças de agentes ou abstração universal de provedores. Introduzir
interfaces pequenas somente para testar rede, relógio, modelos e busca. TypeScript strict,
nomes de estados comuns aos contratos e componentes pequenos; CSS por componentes/estados,
sem biblioteca de design adicionada por conveniência.

## Runtime, agentes e estados

A sessão recebe `session_id`/cookie aleatório e `server_instance_id` gerado no boot; cada conversa
tem `conversation_id` e `epoch`. Apenas um turno/research run mutante por conversa por vez.
Lock curto protege aceitar oferta, selecionar snapshot e encerrar. I/O externa ocorre fora do
lock; o resultado só é aplicado se a conversa continua aberta e o epoch é o mesmo.

LangGraph terá nós de orquestração, recuperação, pesquisador e tutor; LangChain serve a integração
com Gemini e documentos. Começar sem checkpointer/store: compilar grafo sem persistência e passar
estado de conversa mantido em `sessions.py`. A espera por autorização fica na aplicação, entre
execuções do grafo; não exige Agent Server nem interrupt durável. InMemorySaver é alternativa
apenas se um experimento demonstrar necessidade; nesse caso excluir o thread inteiro no fechamento.

O orquestrador pode delegar e avaliar necessidade de pesquisa, mas o guard externo decide se pode
executá-la. Reconhecer pedido explícito usando exclusivamente a mensagem original do usuário
e ação de UI, nunca instruções de documentos ou trechos recuperados. Se a intenção for ambígua,
pedir esclarecimento antes de pesquisar. Oferta referencia turno/assunto, expira com a conversa
e só pode ser aceita uma vez. Recusa marca a oferta como recusada, sem iniciar tarefa.

Pesquisador: descoberta de URLs → SafeFetcher → extração determinística → fontes temporárias.
Tutor: recuperar trechos autorizados e temporários disponíveis → produzir resposta estruturada
com IDs de evidência → validar referências → renderizar. Não expor SQL, seleção ou ingestão como
tools dos agentes. Um ID de citação válido não prova sustentação semântica: isso é avaliado em E6.

Ao encerrar, marcar CLOSED e incrementar epoch antes de cancelar tarefas; remover mensagens,
respostas parciais, fontes, vetores temporários e referências; callbacks atrasados descartam a saída.
O cliente limpa estado React e abre nova conversa. Novo boot invalida todos os IDs de conversa.
IDs desconhecidos retornam 410 sem recriar conteúdo ou conservar tombstones de fontes no banco.

## Pipeline textual e RAG

A regra completa de snapshots, hashes e locators está em [data-model.md](data-model.md).
Validar bytes e origem antes de normalizar; parsear Markdown por blocos; preservar títulos,
listas, tabelas e código. Não usar um LLM para validação, normalização ou chunking.
Texto extraído de HTML vira snapshot estruturado antes de passar pelo mesmo pipeline textual.

Baseline de laboratório: alvo 1.600 caracteres Unicode, teto 2.400 e overlap de até 200 em
fronteiras de blocos. Comparar com 800/1.200 em E3. Não confundir caracteres, tokens e bytes;
validar o orçamento de tokens do modelo antes de chamar a API. Blocos grandes são segmentados
por linhas e depois pontos de código se necessário, mantendo locators contíguos no snapshot.
Manter título/contexto estrutural em metadados e entrada do embedding, sem inventar texto citado.

Perfil inicial de embedding: `gemini-embedding-001`, 768 dimensões, task types de documento/query,
normalização L2 explícita e busca exata por cosseno. Avaliar 1.536 e `gemini-embedding-2` somente
com reembedding e perfil segregado; não assumir mesmo espaço ou mesmos parâmetros de API.
A geração provisória usa `gemini-3.5-flash-lite`; comparar `gemini-3.8-flash` em E2/E6.

SQL recupera apenas versões READY e vetores do perfil ativo; temporárias usam vetores na RAM.
Computar embeddings temporários sob demanda sem gravação local durável. Ordenar separadamente, combinar
por cosseno apenas quando o perfil for idêntico, deduplicar e reservar representação de ambas as
origens quando houver evidência relevante. Baseline top-k=5; comparar 3/8. Nenhum corte de score
é universalmente interpretado como ausência de evidência: calibrar com perguntas respondíveis,
parciais e impossíveis. Nenhum resultado relevante implica resposta de insuficiência.

## Promoção, concorrência e falhas

A rota de seleção recebe apenas ID efêmero e `snapshot_hash` apresentado pela UI. Fora do modelo,
confirmar sessão/conversa aberta, epoch, hash e fonte utilizável. No lock da conversa, copiar
somente o snapshot selecionado e fazer commit curto da autorização/material/operation em SQL.
Esse commit é o ponto de linearização: se fechar a conversa antes dele, retornar 410 e não gravar;
se a seleção foi aceita antes, a ingestão autorizada continua independente da conversa.

Nunca obter de novo a URL para promover. A seleção repetida retorna a operação/material existente,
com unique constraints no banco, inclusive entre cliques concorrentes. Mesmo conteúdo local
reenviado pode reutilizar a versão existente; novo conteúdo no mesmo nome/URL é nova versão,
sem sobrescrever citações antigas. Essa política é proposta técnica revisável.

O executor prepara chunks/embeddings e verifica quantidade, locators, dimensão e valores finitos.
Publicar todos os chunks e atualizar versão ativa/READY na mesma transação. Não manter transação
aberta durante chamadas externas. Promover a versão ativa por comparação atômica do version_number:
uma retentativa antiga não pode substituir uma versão mais nova já READY. Falha ou reinício
antes da publicação deixa versão FAILED/INTERRUPTED, sem chunks recuperáveis. Ao iniciar, marcar
operações queued e running órfãs como interrupted, inclusive queued sem runner_instance_id cujo
processo caiu após o commit da seleção e antes do agendamento. A retomada de conteúdo autorizado
é explícita e idempotente. Versão antiga READY continua
recuperável se uma nova versão falhar. SQL não recebe payloads de fontes não selecionadas,
nem mesmo para registrar erro ou deduplicação.

Usar AsyncSession SQLAlchemy por unidade de trabalho, sem compartilhar sessão entre tarefas.
O executor possui admissão limitada antes de aceitar novos trabalhos; excesso retorna estado
compreensível, sem fila ilimitada. Falha de agendamento após commit marca a operação interrompida
e mantém a autorização já aceita para retry explícito.

## Segurança, privacidade e observabilidade

- API/segredos apenas no backend, sem prefixo `VITE_` para chaves; env ou secret montado read-only.
  Publicar somente loopback; validar Host e Origin, desabilitar CORS aberto, cookie HttpOnly
  SameSite=Strict e token CSRF para mutações. O token identifica a sessão local, sem cadastro.
  Proteger também multipart contra requisições cross-site; não confiar em localhost por si só.
- Upload limitado por streaming de bytes antes de qualquer spool; não usar UploadFile com
  spill para disco para fontes temporárias. Para Markdown autorizado, rejeitar arquivo binário,
  vazio, extensão inválida, UTF-8 inválido e NUL. Nome é metadado, nunca caminho de filesystem.
- Renderizar Markdown com HTML bruto desabilitado, links HTTP(S) validados, imagens remotas
  desabilitadas e `noopener noreferrer`. Não executar scripts, iframes, eventos ou URLs
  javascript/data. CSP e `Cache-Control: no-store` em respostas/conteúdo; sem service worker,
  localStorage, sessionStorage, IndexedDB ou restauração do chat pelo navegador.
- Coleta web valida esquema, host, porta, IP e todos A/AAAA; rejeita endereços não globais,
  redes Compose, localhost, metadata e IPv4 mapeado proibido. Conecta ao IP já aprovado mantendo
  Host/SNI e validação TLS, sem segunda resolução DNS vulnerável. Revalidar cada redirect,
  fallback e retry. Sem proxy de ambiente, cookies ou credenciais herdadas. Usar transporte
  pequeno HTTPCore/HTTPX com APIs públicas; E4 precisa provar a conexão efetiva.
- Retentativas só para erros transitórios e chamadas idempotentes: 2 tentativas totais como
  baseline, backoff limitado, respeitando Retry-After e deadline. Não repetir validação,
  autorização, destino bloqueado, credencial inválida ou citação sem evidência.
  Desabilitar retries automáticos sobrepostos do SDK/LangChain/HTTP: a aplicação possui o
  orçamento e contabiliza cada tentativa, inclusive na correção de schema.
- Sem logs de prompts, respostas, corpos HTTP, queries de busca, títulos/URLs ou hashes de fontes
  temporárias. Allowlist: request_id aleatório, etapa, classe de erro, duração, status e contagem.
  Sanitizar exceções SDK/SQL e desabilitar parâmetros SQL em logs. Fonte selecionada pode ter
  auditoria da autorização em SQL; chat não vira tabela.
- Desabilitar LangSmith, OpenTelemetry de payloads, debug de SDK, HTTP caches e logging de acesso
  com query string. Se LangSmith for experimentado, somente fixtures sintéticas/autorizadas
  e sem dependência para rodar ou apresentar. Capturas/screenshots da demonstração com conteúdo
  não selecionado também não são feitas automaticamente.
  Rejeitar configuração de tracing de payloads no perfil real, inclusive flags legadas como
  LANGCHAIN_TRACING_V2; não depender apenas de uma variável de ambiente com nome novo.
- UI informa antes do uso: perguntas, trechos necessários da biblioteca ou pesquisa e entradas de
  embeddings podem ser enviados à API Gemini; busca envia a consulta ao provedor de descoberta.
  Exibir provedor/modelo configurados e informação de retenção gerida pelo provedor, sem chaves. É informação
  contínua da interface; não adicionar confirmação redundante a um pedido explícito de pesquisa.
  A autorização de envio à API não autoriza guardar a fonte na biblioteca.

## Parâmetros iniciais e experimentos

[research.md](research.md#experimentos-mínimos-e-pontos-de-decisão) define E0–E6 e alternativas.
Propostas para limites de laboratório, ainda revisáveis:

| Recurso | Baseline inicial | Motivo / experimento |
|---------|------------------|----------------------|
| Upload Markdown | 1 MiB por arquivo, até 50 materiais no corpus de ensaio | Detectar gasto e evitar lote irrestrito; E1/E3. |
| HTML | 2 MiB descomprimidos, até 3 redirects, HTTPS preferido e portas 80/443 | Testar amplificação, SSRF e páginas comuns; E4. |
| Pesquisa | 1 consulta, até 5 páginas por execução e 20 fontes temporárias por conversa | Custo e RAM previsíveis; E4. Excesso recusa nova coleta, sem apagar fontes antigas. |
| Texto/conversa | 128 KiB por mensagem, 8 MiB de texto temporário e contexto com orçamento explícito | E5: recusar excesso com explicação; não fazer resumo durável nem descarte silencioso. |
| Concorrência | 1 turno por conversa, 1 ingestão e 2 fetches simultâneos | Facilitar estados e medir contenção; E5. |
| Prazos | fetch 10 s por tentativa, pesquisa 45 s, turno 60 s, ingestão 120 s | Apenas timeouts de ensaio, não metas de latência; E2/E4/E5. |
| Grafo | até 8 passos e 20 chamadas externas por turno; pesquisa tem subteto de 1 busca + até 5 páginas | Incluir geração, embeddings, fetch e todas as tentativas no teto global; E6. |
| Vetores/RAG | dimensão 768, top-k 5, cosseno exato | Menor início comparável; E3 versus 1.536/top-k 3/8. |

Prazos totais prevalecem sobre prazos individuais. Contar toda tentativa no orçamento. Execução
que excede o orçamento é interrompida e não rotulada sucesso. Registrar os ajustes feitos após
experimentos em research.md, sem atribuir aprovação ao usuário que apenas autorizou testar.

## Fatias demonstráveis e reserva

Sem data de apresentação informada, o quadro é uma hipótese de orçamento de **20 dias-pessoa**,
não cronograma acordado. Reestimar após E0/E1 e medir velocidade. Reservar 30% para integração,
correções e ensaio; todas as jornadas confirmadas permanecem na entrega.

| Fatia | Demonstração / saída | Hipótese de esforço |
|-------|----------------------|---------------------|
| F0 | E0–E2, locks/imagens e contratos compatíveis; nenhum dado não autorizado | 2 dias |
| F1 | Markdown → biblioteca → estados → citações rastreáveis; progresso já mostra ingestão | 3 dias |
| F2 | Tutor RAG da biblioteca, insuficiência, referência consultável e encerramento | 3 dias |
| F3 | Oferta/recusa e pedido explícito; busca HTML, tutoria temporária, falha parcial e descarte | 3 dias |
| F4 | Seleção/promoção idempotente, concorrência, falha e biblioteca após reinício | 3 dias |
| F5 | Integração completa, testes de vazamento/SSRF, avaliações e correções | 4 dias |
| F6 | Ensaio da apresentação, recuperação de falhas e conferência de configuração | 2 dias |

E3/E4/E5/E6 acompanham F1–F5, não ficam todos no fim. O gate externo G0 foi retirado por esclarecimento do usuário.
Se a data disponível não comportar o esforço, explicitar opções: ampliar prazo, disponibilizar
mais tempo de implementação ou negociar uma redução com o usuário. Não remover pesquisa,
tutoria temporária, seleção, rastreabilidade ou falhas silenciosamente. Demonstração com doubles
pode apoiar desenvolvimento, mas não comprova integração Gemini/busca e não substitui o escopo.

## Validation e entrega ao próximo comando

Matriz de testes em research.md e exemplos em quickstart.md. Pytest deve provar as garantias
contratuais com fixtures determinísticas; testes externos são separados e explícitos. Retrieval
mede relevância dos trechos, agentes medem comportamento e citações; não existe avaliador
pedagógico. Revisão humana de sustentação faz parte do conjunto pequeno, sem criar outro agente.

Critérios de passagem para implementação: contratos revistos; retenção local e aviso externo definidos para o fluxo real;
E1 comprova conjunto instalado; parâmetros experimentais estão identificados; nenhum documento
parcial aparece no RAG; invariantes de autorização/descarte não são compensadas por média de score.
Tarefas de scaffolding e fixtures podem preceder E0; não marcar demonstração integral pronta
enquanto os critérios de aceite ou testes reais necessários estiverem pendentes.

## Complexity Tracking

| Added Complexity | Why Needed | Simpler Alternative Rejected Because |
|------------------|------------|--------------------------------------|
| Transporte HTTP com IP validado | Evitar SSRF e rebinding na coleta | Validar URL e depois fazer fetch comum reabre DNS e não cumpre a proteção. |
| Alembic e perfil vetorial explícito | Evoluir esquema/dimensão sem misturar espaços | create_all e atualização implícita não preservam migrações e compatibilidade. |
| Epoch/lock por conversa e constraints SQL | Tornar fechar/selecionar/repetir verificáveis | Apenas esconder botões não impede callbacks tardios ou cliques concorrentes. |

Não há microserviços, fila distribuída, banco adicional, auth multiusuário, reranker ou índice
aproximado aprovado por este plano. Parâmetros e organização podem ser revistos com evidência.
