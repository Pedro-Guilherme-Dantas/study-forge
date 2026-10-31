# Research: StudyForge — decisões e experimentos

## Revisão autorizada: observabilidade para apresentação

Atualização de 2026-10-30: captura detalhada autorizada pelo usuário via
`STUDYFORGE_TRACE_CONTENT`. Perguntas, trechos, prompts e respostas podem ser enviados ao
LangSmith, com aviso de armazenamento remoto, mascaramento das chaves configuradas e limites.
Sem persistência local de conteúdo. Seis árvores detalhadas indexadas, incluindo uma jornada
HTTP real com Gemini em schema isolado. Uma leitura adicional recebeu 429: limites de consulta
do provedor também afetam diagnóstico. Não há retry ilimitado nem dependência do tracing
para responder. Evidência em `evidence/langsmith-content.md`.

LangSmith opcional com spans explícitos de metadados operacionais, captura automática de
conteúdo bloqueada e divulgação externa na interface. SDK 0.14.14 conferido na imagem;
cliente assíncrono com uma tentativa e prazo finito, sem novo serviço. Exportação/indexação
de cinco árvores de fixture confirmadas via API. Guia: `docs/observabilidade-langsmith.md`;
evidência: `evidence/langsmith.md`. Referências oficiais:
https://docs.langchain.com/langsmith/trace-without-env-vars e
https://docs.langchain.com/langsmith/log-traces-to-agent (`tracer_session_name` compatível).

**Data**: 2026-10-28. Pesquisa documental em fontes primárias; nenhum pacote instalado,
modelo chamado ou benchmark executado neste comando. A data de consulta não garante acesso
ao modelo na conta do usuário. As versões abaixo são candidatas; E1 produzirá locks reproduzíveis.

## R0. Retenção local e envio externo — revisão 2026-10-29

O usuário esclareceu que a exigência de não persistir fontes não selecionadas e conversas vale para o armazenamento local do StudyForge. O gate G0 e a exigência de comprovante de retenção zero foram retirados. O envio às APIs Gemini e busca segue as políticas dos provedores e deve ser informado na interface. Não prometer apagamento remoto ao encerrar a conversa. Credenciais no backend, limites de execução e testes de integração continuam necessários. Biblioteca e persistência indireta local continuam sob controle explícito do usuário.

## R1. Versões candidatas e compatibilidade

**Decisão**: começar com candidatos estáveis observados nas fontes, resolver dependências em
contêiner, registrar versões transitivas e digests. Não usar latest no artefato demonstrado.

| Componente | Candidato documental | Fonte primária |
|------------|-----------------------|----------------|
| React / React DOM | 19.3.1, par de versões igual | [npm React](https://registry.npmjs.org/react/latest) |
| TypeScript | 7.0.2 | [npm](https://registry.npmjs.org/typescript/latest) |
| Vite | 8.3.5 | [release](https://github.com/vitejs/vite/releases/tag/v8.3.5) |
| Node | 24.22.1 LTS | [release](https://nodejs.org/en/blog/release/v24.22.1), [ciclo](https://nodejs.org/en/about/previous-releases) |
| Python | 3.14.10 | [downloads](https://www.python.org/downloads/) |
| FastAPI | 0.162.0 | [PyPI](https://pypi.org/project/fastapi/0.162.0/) |
| Pydantic | 2.14.1 | [PyPI](https://pypi.org/project/pydantic/) |
| SQLAlchemy | 2.1.6 | [changelog](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html) |
| pytest | 9.2.0 | [PyPI](https://pypi.org/project/pytest/) |
| LangChain | 1.4.7 | [PyPI](https://pypi.org/project/langchain/) |
| LangGraph | 1.2.18 | [PyPI](https://pypi.org/project/langgraph/) |
| langchain-google-genai | 4.4.2 | [PyPI](https://pypi.org/project/langchain-google-genai/) |
| google-genai | 2.33.0 | [PyPI](https://pypi.org/project/google-genai/) |
| PostgreSQL | linha 18; minor 18.6 documentada | [versões suportadas](https://www.postgresql.org/support/versioning/) |
| pgvector / imagem | 0.8.7 / 0.8.7-pg18-bookworm | [README e Docker](https://github.com/pgvector/pgvector#docker) |
| pgvector Python | 0.5.1 | [PyPI](https://pypi.org/project/pgvector/) |
| Compose | plugin 5.6.1 como referência documental | [releases](https://github.com/docker/compose/releases) |
| Trafilatura | 2.3.1 | [PyPI](https://pypi.org/project/trafilatura/) |
| markdown-it-py | 4.2.0 | [PyPI](https://pypi.org/project/markdown-it-py/4.2.0/) |
| HTTPX / HTTPCore | 0.28.1 / 1.0.9 | [HTTPX](https://pypi.org/project/httpx/), [HTTPCore](https://pypi.org/project/httpcore/1.0.9/) |

Psycopg 3 é o driver proposto e Alembic a proposta de migração; resolver patches compatíveis
em E1, não inventar versão exata sem o lock.
[Psycopg](https://www.psycopg.org/psycopg3/docs/),
[Alembic](https://alembic.sqlalchemy.org/en/latest/).
A integração LangChain usa a família google-genai; não misturar SDK legado por conveniência.
[Integração oficial](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai).

**Motivo**: usar documentação verificável e uma base de build controlada. Python/Node anteriores
a essas linhas podem ser alternativas se E1 demonstrar incompatibilidade; não trocar versão de
uma dependência isoladamente sem regenerar/verificar o conjunto. Versão realmente embarcada
na imagem PostgreSQL deve ser consultada; tag da extensão não comprova minor do servidor.

## R2. Modelos e perfil de embeddings

**Decisão provisória**: geração baseline `gemini-3.5-flash-lite`; comparar `gemini-3.8-flash`.
Confirmar IDs e recursos no endpoint/conta efetivo, especialmente se E0 escolher outro endpoint
Gemini. Não fixar modelo preview por ser o mais recente.
[Catálogo](https://ai.google.dev/gemini-api/docs/models),
[Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
[Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash).

**Motivo**: iniciar a comparação com uma opção econômica e outra de capacidade maior; só E2/E6
dirá qual atende tutoria, português, chamadas estruturadas e citações com custo/latência aceitáveis.

**Embedding inicial**: `gemini-embedding-001`, dimensão 768, RETRIEVAL_DOCUMENT/RETRIEVAL_QUERY
e normalização L2 explícita. Alternativas: 1.536 no mesmo modelo e `gemini-embedding-2`.
O guia distingue limites e formas de instruir a tarefa; não aplicar task_type de 001 ao 2.
[Guia oficial](https://ai.google.dev/gemini-api/docs/embeddings).

**Reprodutibilidade**: texto/chunks/locators precisam ser idênticos para input e pipeline fixos;
vetores reais são saídas externas e podem variar. Registrar modelo retornado quando disponível,
provider, dimensão, task modes, normalização, template e época de indexação. Não alegar que um
hash do texto torna o embedding determinístico. Avaliar variação de ranking repetindo chamadas;
testes unitários usam vetores fixos, integrações reais verificam norma/dimensão e ranking tolerante.

## R3. Recuperação persistida e temporária

**Decisão**: cosseno exato no PostgreSQL para versões READY, mais ranking em RAM das temporárias
compatíveis. Começar com top-k 5 e medir 3/8; sem HNSW ou reranker inicialmente.

**Motivo**: volume inicial pequeno, ranking auditável e ausência de índice adicional sem evidência.
A biblioteca Python documenta integração SQLAlchemy/driver; provar transações e ordenação em E3.
[pgvector Python](https://github.com/pgvector/pgvector-python#sqlalchemy).

**Alternativas**: HNSW ou combinação lexical-vetorial no mesmo PostgreSQL se E3 demonstrar
necessidade. `vector` e seus índices têm limites diferentes: armazenamento aceita até 16.000
dimensões, índices vector HNSW/IVFFlat até 2.000; um vetor 3.072 não recebe automaticamente
HNSW vector_cosine_ops. [Limites e busca](https://github.com/pgvector/pgvector).
Mudar modelo/dimensão exige perfil e reembedding separado; não comparar espaços distintos.

## R4. Descoberta, extração e SSRF

**Decisão provisória**: Brave Web Search para descobrir URLs; coletar HTML localmente.
Alternativa: Tavily básico sem resposta gerada ou raw_content. Não implementar ambos antes
do experimento nem usar grounding integrado como substituto do pesquisador.
[Brave](https://api-dashboard.search.brave.com/app/documentation/web-search/query),
[Tavily](https://docs.tavily.com/documentation/api-reference/endpoint/search).

**Motivo**: separar descoberta de obtenção, extração e autorização. Snippet não prova leitura
da página; resultados sem corpo extraível não fundamentam tutoria como fonte obtida.
Condições de conta, uso e retenção devem ser verificadas em E0/E4.

Trafilatura extraction-only sobre HTML já obtido: candidato output_format=markdown,
include_comments=False, include_tables=True, formatação/links preservados e deduplicate=False.
Fixar essas flags no fingerprint e testar código/tabelas. Não usar fetch_url do extrator.
Alternativa BeautifulSoup exige regras próprias de boilerplate.
[Trafilatura](https://trafilatura.readthedocs.io/en/latest/corefunctions.html),
[extração](https://trafilatura.readthedocs.io/en/stable/extraction-overview.html).
Markdown-it-py fornece tokens com map de linhas; HTML bruto deve ser desabilitado.
[Tokens](https://markdown-it-py.readthedocs.io/en/latest/using.html),
[segurança](https://markdown-it-py.readthedocs.io/en/latest/security.html).

SafeFetcher conecta a IP aprovado; validar DNS e depois chamar httpx.get(host) não fecha rebinding.
Resolver A/AAAA, rejeitar conjunto com qualquer IP não global, validar cada salto e fallback,
não herdar proxies nem cookies, limitar corpo descomprimido e preservar Host/SNI/certificado.
Esse adaptador é pequeno e tem testes de conexão, sem monkeypatch global de DNS.
[OWASP SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html),
[transportes HTTPX](https://www.python-httpx.org/advanced/transports/),
[backend HTTPCore](https://www.encode.io/httpcore/network-backends/),
[SNI](https://www.encode.io/httpcore/extensions/#sni_hostname),
[variáveis HTTPX](https://www.python-httpx.org/environment_variables/).
Usar is_global e política explícita, não apenas not is_private.
[Python ipaddress](https://docs.python.org/3/library/ipaddress.html).

## R5. Estado, publicação e acesso

**Decisão**: grafo sem checkpoint/store durável; memória de conversa na aplicação, um worker.
Esperar confirmação fora do grafo. Alternativa InMemorySaver exige apagar todos os checkpoints
do thread e buffers no encerramento; não apenas remover mensagens do último estado.
[Persistência LangGraph](https://docs.langchain.com/oss/python/langgraph/persistence),
[gerenciamento de memória](https://docs.langchain.com/oss/python/langgraph/add-memory).

**Motivo**: a clarificação escolheu descarte, sem replay após reinício. Sem dependência de
LangSmith ou Agent Server. Tarefas autorizadas de ingestão são retomáveis pela biblioteca;
tarefas de conversa não são restauradas.

**Acesso confirmado**: somente localhost. Sem contas; sessão local opaca, CSRF e Host/Origin
impedem que outro site abuse da API do navegador. Build React servido pelo app; Vite dev é
opcional e usa proxy. Publicar loopback no host e nenhuma porta do banco.
[Compose networking](https://docs.docker.com/compose/how-tos/networking/).
Não ampliar para LAN como mero ajuste de porta: exige revisão de autenticação e transporte.

**Identidade/publicação**: snapshot selecionado imutável, chaves únicas, autorização antes de
gravar e publication transaction após embeddings completos. Bibliotecas/versões são consultadas
via READY + active_version; drafts não entram em retrieval. Regras detalhadas em data-model.md.

## Experimentos mínimos e pontos de decisão

Os valores abaixo são orçamento inicial de investigação autorizado pelo pedido de planejamento,
não metas de qualidade aprovadas. Evidências e ajustes serão produzidos na implementação.

| Experimento | Menor prova útil | Saída / ponto de decisão |
|-------------|------------------|--------------------------|
| E0 — retenção e ambiente | Revisar termos/configuração reais de geração, embeddings e descoberta; verificar logs, caches, swap, volumes e frontend | Verificação de retenção local e aviso de envio externo, sem gate de retenção zero. Nenhuma chave ou documento em relatório. |
| E1 — versões/Compose | Build React, tsc separado, imports Python, migração e conexão PostgreSQL real | Locks, hashes, digests e lista de versões efetivas; incompatibilidade documentada antes de fixar. |
| E2 — Gemini | 5 casos por modelo: suporte, lacuna, conflito, instrução hostil, saída estruturada; 3 execuções de um caso | Validade de esquema/citações, latência, custo/usage e variação; escolha provisória do modelo por papel. |
| E3 — pipeline/vetores | 6 Markdown + 6 HTML próprios, dois tamanhos de chunk; vetores conhecidos e embeddings reais; 12 perguntas rotuladas | Hash/locator idêntico para input fixo; dimensão/norma; Recall@k/MRR e ranking comparado; escolher perfil/chunking/top-k provisórios. |
| E4 — descoberta/fetch | 5 consultas PT-BR, 6 tipos de HTML, negativos SSRF/redirect/rebinding/gzip | URLs úteis realmente extraídas, fidelidade estrutural, conexões proibidas impedidas e custo/tempo; selecionar um provedor. |
| E5 — publicação/descarte | Dois selects concorrentes, fechar versus selecionar, restart antes de agendar e durante ingestão, falha no último embedding, retry v1 após v2 READY | Uma autorização/versão/operação, sem queued órfã ou regressão da versão ativa; zero documentos parciais e nenhum marcador temporário em SQL/logs/arquivos. |
| E6 — agentes e jornada | 12 casos comportamentais + jornada US1→US5 em ambiente integrado | Supervisão, consentimento de busca, não persistência, citações, insuficiência e estados corretos; relatório de desvios. |

Não comparar os dois modelos de embedding sem reconstruir corpus inteiro por perfil. A execução
real depende de credenciais e configuração; ensaios com doubles não comprovam integração externa.

## Testes e avaliação separados

**Determinísticos com pytest**:
- validação Markdown, Unicode/LF, código/tabelas, golden chunks e locators; input repetido igual;
- autorização ausente não chama ingestão; fonte expirada/hash diferente não escreve; cliques
  repetidos e disputa fechamento/promoção com relógio e barreiras controladas;
- destinatário privado, DNS público+AAAA privado, rebinding, redirects, retry e descompressão:
  afirmar que o transporte não conectou, não apenas que lançou erro depois;
- cliente modelo falso devolve citação inexistente, quote inventada e tool proibida; validador
  rejeita e resposta não sinaliza conclusão válida;
- PostgreSQL real em Compose: unique constraints, rollback, restart, perfil incompatível,
  vetor inválido e filtro READY, sem substituir por SQLite;
- marker exclusivo colocado em HTML temporário atravessa conversa e erro; inspecionar todas as
  tabelas, logs de containers, artefatos de teste e caches; marker não pode aparecer duravelmente;
- fechar/aplicar callback atrasado e reiniciar invalida conversas; biblioteca preservada;
- testes HTTP por TestClient e banco real; sessão, CSRF, Origin, Host, limites e envelopes.

**Retrieval**: corpus inicial de 12 documentos próprios, com tópicos próximos e distratores.
12 perguntas iniciais: 6 sustentadas, 2 parciais, 2 sem evidência e 2 que exigem combinar fontes.
Anotar IDs de trechos relevantes, relevância 0/1/2 e localizadores antes de olhar resultados.
Medir Recall@3/5/8, MRR, proporção de trechos irrelevantes e cobertura de origem; precisão por
query e falhas de locator. Perguntas sem evidência avaliam abstinência, não entram como acerto
de Recall apenas porque retornaram algum trecho. Expandir somente ao descobrir lacunas.

**Agentes**: 12 casos próprios, cobrindo pedido explícito, oferta aceita, recusa, espera,
evidência disponível, lacuna, conflito, instrução hostil, referência inválida, fonte expirada,
limite e seleção indevida. Asserts de ferramenta/efeito são determinísticos com doubles.
Rodada real pequena compara respostas e exige revisão humana de sustentação e utilidade;
LLM-as-judge não substitui essa revisão nem vira agente pedagógico.

**Citações**: validade estrutural (ID pertence ao evidence set, fonte disponível e quote extraída
do span) é verificada por código; sustentação da afirmação e ausência de extrapolação são
verificadas por pares de pergunta/resposta/evidência na avaliação e revisão. Limitar uma tentativa
de correção de schema dentro do orçamento; se continuar inválido, erro/insuficiência explícito.

**Metas**: registrar baseline e propor alvos depois. As propostas 80%/90% da especificação
continuam propostas. Nenhum erro de autorização, SSRF, retenção ou publicação parcial é aceito
como compensável por média de qualidade. Métricas e relatórios não conservam conteúdo real
não selecionado; persistir somente resultados de fixtures próprias/autorizadas.

## Registro de decisão e revisão

Após cada E: input autorizado, config/pipeline/profile, versões, resultado observável, limite da
evidência e escolha mantida/alterada. Acrescentar motivo e alternativa simples considerada.
Não marcar experimento como realizado apenas porque há um plano ou um teste que usa double.

No planejamento inicial não havia benchmark real nem data de apresentação fornecida.
O plano usa orçamento relativo e reserva de integração. A exigência externa G0 foi
retirada na emenda aprovada em 2026-10-29; ver resultados posteriores abaixo.

## Resultado E1 — implementação em 2026-10-28

Bootstrap executado com Python 3.14.10, Node 24.22.2 e PostgreSQL 18.6. Build React/TypeScript e imports Python passaram; teste pgvector real: 1 passed. Locks/hash/digests e limitações em evidence/E1-runtime.md. Gemini/busca e G0 não foram validados por esse resultado.

## Implementação e verificações locais — 2026-10-29

O usuário solicitou continuar com fixtures, pois ainda não tem endpoint/credenciais Gemini. Não houve chamada real Gemini/Brave. Registro histórico, superado pelo esclarecimento de 2026-10-29: G0 foi retirado; E2 e partes externas de E3/E4/E6 não foram executadas. Os parâmetros permanecem experimentais.

Biblioteca, grafo de três papéis, pesquisa temporária, promoção e navegação operacional estão implementados. As verificações locais e suas limitações constam em [local-evaluations](evidence/local-evaluations.md) e [readiness](evidence/readiness.md). A migração 0002 acrescenta SelectionGrant e metadados de extração; DDL da 0001 permanece congelado. A API ganhou consulta de coleção de chunks para inspeção na biblioteca, documentada no contrato.

O transporte usa APIs públicas de [HTTPCore](https://www.encode.io/httpcore/network-backends/) para conexão pinada e preserva [SNI](https://www.encode.io/httpcore/extensions/). A extração usa somente bytes já obtidos e a API de [Trafilatura](https://trafilatura.readthedocs.io/en/latest/corefunctions.html). Na versão instalada, max_tree_size levanta ValueError de depreciação; o argumento foi removido e o corpo de entrada permanece limitado. Não há fetch dentro da extração.

## Experimentos reais e corpus ampliado — 2026-10-29

A chave Gemini foi disponibilizada via .env; somente presença/configuração foram expostas nas saídas. Embeddings reais funcionaram. A geração revelou schema incompatível (additional_properties), corrigido com response_json_schema e validação Pydantic local. Timeout individual foi alinhado ao orçamento de 60 s. Retentativas transitórias são limitadas a duas, contadas no orçamento e respeitam RetryInfo quando cabe no prazo. Requisições inválidas/autenticação não são repetidas.

gemini-3.5-flash-lite respondeu em 6/10 casos; gemini-3.8-flash falhou nos cinco casos tentados e a repetição foi interrompida. gemini-2.5-flash-lite completou 10/10 chamadas com JSON/citações válidos, mas apenas 8/10 classificações esperadas: o caso parcial omitindo meiose foi indevidamente tratado como sustentado. Não se declara avaliação comportamental integral aprovada. Uma jornada HTTP real com Markdown/embedding/RAG/tutor/citação/fechamento passou com esse candidato em schema de teste isolado. O prompt foi reforçado genericamente para cobrir todas as partes da pergunta; tentativas posteriores de validação encontraram indisponibilidade externa, sem aprovação presumida.

A avaliação E3 inicial era pequena demais para calibrar chunking. Por pedido do usuário, o corpus principal foi substituído por 12 artigos completos da Wikipédia (512.403 caracteres; 65.519 palavras), com revisões, autoria, licença CC BY-SA 4.0 e hashes. O corpus sintético foi preservado. Novas perguntas incluem seções, múltiplos documentos e ausência de evidência. O ensaio longo detectou timeout em lote 100 e 429 em lote 32 sem espaçamento. O baseline com lotes menores e pausas está sendo executado; resultados e limitações em evidence/E3-retrieval.md.

Busca Brave ainda sem chave. SafeFetcher foi exercitado realmente contra páginas públicas de ensaio: example.org (577 bytes HTML, 156 caracteres extraídos) e tutorial Python (140.178 bytes HTML, 36.621 caracteres extraídos) funcionaram; uma página FastAPI foi rejeitada por formato retornado não aceito. Isso não comprova descoberta Brave.

## Consolidação posterior — 2026-10-29

O usuário manteve gemini-3.5-flash-lite; 3.1 somente se limites de uso exigirem.
Brave foi configurado e comprovado na jornada real completa, sem exposição de
chaves. Aplicação em modo real, readiness OK. E2/E6 revisado: 9 respostas corretas
nos cinco casos × duas repetições e uma indisponibilidade 503; manter falhas na
contagem. E3 longo baseline: 345 chunks, documentos Recall@5 98,21%, passagens
92,86%; 800/768 produz 744 chunks mas a API interrompeu a medição por 429.
1536 longo pendente. Não há justificativa para trocar top-k/chunking com essa
comparação incompleta. E4/E5 e contratos têm relatórios próprios em evidence/.
Nenhuma meta numérica foi promovida a requisito aprovado. Segurança e retenção
local verificadas no ambiente efetivo com as limitações registradas.
