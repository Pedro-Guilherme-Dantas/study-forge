# Data Model: StudyForge — MVP

**Data**: 2026-10-28. Modelo proposto para revisão, coerente com [spec.md](spec.md) e
[plan.md](plan.md). PostgreSQL é o único banco. Objetos efêmeros abaixo não são tabelas.

## Invariantes

1. Somente upload validado ou snapshot web selecionado pode originar conteúdo persistido.
2. Qualquer gravação web exige autorização explícita verificada pela aplicação, fora do modelo.
3. Retrieval consulta apenas a versão ativa READY, com chunks/vetores completos e perfil compatível.
4. Conversas, resultados temporários, ofertas e respostas nunca têm linha persistente de conteúdo.
5. Fechamento/reinício invalida IDs e callbacks efêmeros; conteúdo selecionado já autorizado pode
   concluir ingestão sem depender da conversa. Seleção aceita não equivale a ingestão concluída.
6. Idempotência de seleção não depende da memória do agente nem apenas do header HTTP.
7. Trocar pipeline ou espaço vetorial cria versão/perfil novo, preservando referências anteriores.

## Fronteira de armazenamento

| Dado | Local | Retenção / regra |
|------|-------|-----------------|
| Material local enviado e versões | PostgreSQL | Biblioteca persistida; somente versões completas entram no RAG. |
| Snapshot web selecionado e autorização | PostgreSQL | Apenas o snapshot escolhido; conservar origem e identidade. |
| Chunks e vetores de material autorizado | PostgreSQL | Perfil/versionamento explícitos, publicação transacional. |
| Operação de ingestão autorizada | PostgreSQL | Status, material, tentativa e código sanitizado; sem conteúdo temporário alheio. |
| Texto HTML bruto não selecionado, extração, snippets, URL/título e vetores temporários | RAM do backend | Até fechar conversa ou reiniciar; nunca em volume, cache HTTP ou SQL. |
| Perguntas, respostas, citações, ofertas, tarefas de conversa | RAM backend e estado React | Toda conversa descartada no fechamento/reinício; sem storage do navegador. |
| Diagnóstico durável | Saída allowlisted | Só ID aleatório, etapa, classe de erro, duração, status e contagens. |
| Payload enviado a terceiros | Serviço externo | Políticas do provedor; informar envio externo, sem exigir descarte remoto. |

Auditoria de fonte selecionada não grava a pergunta, título da conversa ou cópia de mensagens.
Metadados de fonte não selecionada não são registrados em SQL para criar um catálogo indireto.

## Entidades persistidas propostas

### Material

- `id: UUID`; `source_kind: markdown_upload | selected_web`.
- `origin_key: text`: identificação estável da origem, única por source_kind.
  Web: URL canônica efetiva validada. Upload: nome normalizado seguro como metadado de origem.
- `display_name`, `original_url`, `effective_url` opcionais conforme origem; apenas autorizados.
- `active_version_id: UUID?`; `status: processing | ready | failed | interrupted`;
  `created_at`, `updated_at`.
- Constraints: unique(source_kind, origin_key); active_version pertence ao mesmo material e está
  READY. Consultas e transações devem impor a relação, não confiar em dados do cliente.

Se uma nova versão falhar, a versão ativa READY anterior mantém o material disponível. O estado
da nova tentativa aparece na operação/version, sem reclassificar a versão antiga como falha.

**Proposta de duplicação**: mesmo nome/origem e mesmo input reutilizam a versão; mesmo nome/URL
com input diferente cria nova versão; nomes diferentes podem representar origens diferentes.
Não deduplicar globalmente apenas pelo texto: isso perderia proveniência. Versões anteriores
não são sobrescritas. A política é revisável após ensaios e não é uma resposta atribuída ao usuário.

### MaterialVersion

- `id: UUID`, `material_id`, `version_number` monotônico por material.
- `input_snapshot_text`: Markdown UTF-8 enviado ou Markdown estruturado extraído do HTML,
  exatamente o conteúdo autorizado. `input_sha256` identifica esse snapshot de entrada.
- `raw_capture_sha256`: hash dos bytes capturados. Para upload representa o arquivo recebido;
  para web identifica a captura HTML, que não é persistida neste desenho.
- `normalized_text`, `normalized_sha256`, `pipeline_fingerprint`, `pipeline_config`.
- `extractor_name/version/config` e `obtained_at` para web; `selected_at`/grant vinculado.
- `embedding_profile_id`, `expected_chunk_count`, `published_chunk_count`.
- `state: processing | ready | failed | interrupted`, `failure_code?`.
- `created_at`, `ready_at?`; unique(material_id, version_number).
- Chave idempotente unique(material_id, input_sha256, pipeline_fingerprint, embedding_profile_id).
  Config não muda em uma operação em curso; mudanças iniciam outra versão.

Reservar version_number sob lock da linha Material; não calcular MAX+1 sem exclusão mútua.
Na publicação, atualizar active_version_id somente se a versão candidata for mais nova que a
ativa atual e estiver READY. Retry antigo pode concluir e ficar consultável por sua referência,
mas não faz regredir a versão ativa. Testar v1 falha → v2 READY → retry v1 READY.

Para HTML guardar o snapshot extraído selecionado, metadados e hash da captura. Sem os bytes HTML
originais persistidos não é possível reproduzir a extração original; é possível reproduzir
normalização/chunking do snapshot. Não apresentar hash como substituto do arquivo não guardado.
O snapshot não é atualizado por refetch automático.

### SelectionGrant

- `id: UUID`, `material_version_id` ou chave de versão em criação, `selected_at`.
- `input_sha256`, `source_origin_key`, `raw_capture_sha256`, `obtained_at`.
- `action: explicit_user_selection`; actor constante local_personal_user, sem tabela de contas.
- Chave única da versão autorizada; repetições referenciam o mesmo grant.
- Não conservar conversation_id, offer_id, mensagens ou temporários não escolhidos como prova.
  A prova é o registro da ação aceita pelo endpoint protegido e sua identidade de conteúdo.

### Chunk

- `id: text` determinístico; `material_version_id`, `ordinal`.
- `text` igual a normalized_text[start_char:end_char], não uma paráfrase.
- `start_char`, `end_char`: pontos de código Unicode, intervalo [início, fim).
- `start_line`, `end_line`: linhas 1-based inclusivas no snapshot de referência indicado.
- `section_path: list[str]`, `block_kind`, `block_index`, `parent_block_id?`.
- `source_locator`: união discriminada markdown_original | html_extracted_snapshot.
- `chunk_sha256`, `pipeline_fingerprint`, `embedding_profile_id`, `embedding: vector(d)`.
- unique(material_version_id, ordinal); bounds válidos e texto não vazio; vetor finito,
  dimensão do perfil e norma não nula. A mesma versão não mistura perfis.

### EmbeddingProfile

- `id/fingerprint`, provider/endpoint lógico, modelo solicitado/versão retornada se disponível.
- `dimensions`, `document_task`, `query_task`, `normalization`, `input_template_hash`.
- `created_at`, `state: experimental | active | retired`.
- Baseline vector(768). Mudar dimensão exige migração explícita ou coluna/tabela de estágio no
  mesmo PostgreSQL e troca controlada de perfil após reconstrução. Não usar array sem checagem
  para misturar dimensões; comparar resultados apenas dentro do mesmo espaço.

No MVP, mudar a configuração de embedding com acervo existente e perfil incompatível produz
erro de configuração, sem sobrescrever vetores. Experimentos usam schemas de teste isolados.
Se for necessário migrar o acervo real, projetar reembedding explícito e troca atômica do perfil
e dos ponteiros ativos depois da reconstrução completa, preservando a versão anterior até lá.
Não implementar migração quente de múltiplos perfis antes de demonstrar essa necessidade.

### IngestionOperation

- `id: UUID`, `material_id`, `material_version_id`, `grant_id?`.
- `state: queued | running | succeeded | failed | interrupted`.
- `stage: validate | normalize | chunk | embed | publish`, `attempt`, `error_code?`.
- `created_at`, `started_at?`, `finished_at?`, `runner_instance_id?`.
- unique(material_version_id) para operação lógica; tentativas incrementais mantêm esse ID.
- Sem stacktrace/payload de fornecedor; logs não reproduzem SQL parameters ou textos.

## Objetos efêmeros em memória

### Session e ConversationState

Session: ID aleatório, token CSRF, server_instance_id e ponteiro para conversa ativa.
ConversationState: conversation_id, epoch, OPEN/CLOSED, mensagens, respostas parciais,
ofertas, pesquisas, temporários, citações e orçamento. Sem serialização para disco.
Estado da aplicação é a memória do grafo, sem checkpointer PostgreSQL.
Um tombstone sem conteúdo pode existir apenas na RAM para responder 410; após reinício,
qualquer ID inexistente também recebe 410.

### ResearchOffer e ResearchRun

Offer: offer_id, turn_id, assunto proposto, epoch, awaiting/accepted/declined.
Somente aceita oferta da conversa/turno corretos, uma vez. Pedido explícito não cria oferta.
Run: research_id, status running/succeeded/partial/empty/failed/interrupted, contadores,
fontes e códigos sanitizados. Falhas de fonte não autorizam persistir seus metadados.

### TemporarySource

source_id imprevisível, conversation_id/epoch, original_url/effective_url, title,
obtained_at, raw_capture_sha256, input_snapshot_text/input_sha256, normalização/chunks/locators,
perfil/vetores opcionais e estado available/unavailable. Selected aponta material/operation
autorizados; os dados não selecionados continuam só na RAM. Ao fechar, todos os objetos da
conversa são removidos; o banco mantém somente o material/grant já aceito.

### Citation e TurnResult

Citation: citation_id, turn_id, scope library/temporary, material_version_id/chunk_id
ou temporary_source_id/snapshot_hash/chunk_id, locator, quote e indicação de disponibilidade.
TurnResult: status running/complete/partial/insufficient/awaiting_research_consent/failed,
answer, citations e offer opcional. Nenhum desses resultados vai a uma tabela de chat.

## Pipeline determinístico e localização

1. **Validate**: byte budget por stream; extensão .md, UTF-8 estrito, conteúdo não vazio e NUL/
   sinais de binário rejeitados para upload. HTML só pelo SafeFetcher, Content-Type suportado
   e limite descomprimido. Nome do arquivo não decide validade nem vira caminho.
2. **Snapshot**: conservar bytes de upload como texto UTF-8 original autorizado; para HTML,
   extrair títulos/listas/tabelas/código em representação estruturada Markdown na RAM.
   raw_capture_sha256 é calculado antes de decodificar/extrair. Encoding e config são registrados.
3. **Normalize**: remover BOM da representação canônica, CRLF/CR→LF e Unicode NFC. Preservar
   indentação, tabs, espaços relevantes de Markdown/código e hard breaks; não colapsar whitespace
   globalmente. Mapear intervalos/linhas da representação normalizada ao snapshot de entrada.
4. **Parse**: markdown-it-py com HTML bruto desabilitado; tokens/map fornecem blocos e linhas.
   Manter section_path e tipo do bloco. Normalização e parsing não executam links nem conteúdo.
5. **Chunk**: regras de blocos, alvo/teto/overlap explícitos. Preservar blocos até o teto; dividir
   blocos grandes por linhas, depois por pontos de código se preciso. Não sintetizar texto citado
   para fechar fences; marcação de exibição pode indicar continuação e linguagem em metadados.
   Contexto de título usado em embedding é prefixo separado, não parte da quote.
6. **Identity**: SHA-256 dos bytes UTF-8 canônicos; pipeline_fingerprint é hash de JSON canônico
   ordenado com versões/config de extractor, parser, normalizador, chunker e parâmetros.
   chunk_id = SHA-256(version_key + pipeline_fingerprint + ordinal + start/end + chunk_sha256).
   Os chunks temporários usam snapshot_key; na promoção IDs de versão podem mudar com relação
   preservada ao snapshot, sem alterar quotes ou spans.
7. **Embed**: enviar entrada definida pelo perfil, verificar dimensões, finitude e norma;
   cache só para conteúdo autorizado no SQL ou temporário na RAM. Não prometer vetores bit a bit
   iguais entre chamadas externas. Perfil e template identificam o espaço efetivamente usado.
8. **Publish**: validar conjunto completo; gravar chunks/vetores e marcar READY/active_version
   na mesma transação. Não executar chamadas de rede mantendo essa transação aberta.

Markdown tem linhas do arquivo original via mapa. HTML tem URL + hash de captura +
section_path/block_index e linhas/offsets no snapshot extraído; esses offsets não são DOM
nem garantem que o site remoto ainda tenha o mesmo texto. A API informa locator_kind.
JSON usa índices Unicode code points; o frontend converte para offsets UTF-16 ao destacar.
Citação deriva da fatia armazenada, não de offsets enviados pelo modelo.

## Concorrência e transições

**MaterialVersion**: processing → ready | failed | interrupted. Retry explícito pode tentar
a mesma versão failed/interrupted, sem duplicar. Uma versão READY é imutável.

**Conversa**: OPEN → CLOSED; invalidar epoch antes de cancelar e liberar objetos. Callbacks
carregam epoch e descartam saídas se ele divergir. Não recriar conversa ao receber ID velho.

**Selecionar versus fechar**:
- no mesmo lock, verificar OPEN/epoch/hash, escolher snapshot e persistir grant + material +
  versão/operation autorizados em transação curta; liberar o lock após esse commit;
- commit antes do fechamento: autorização aceita, ingestão pode continuar. Fechamento primeiro:
  410, sem nova gravação de conteúdo. Falha de commit não concede autorização;
- não segurar lock durante fetch/embedding; resultados tardios nunca restauram dados efêmeros.

**Duas seleções**: mesma chave retorna material/operation existentes. Unique constraints resolvem
concorrência mesmo se futuramente houver mais de um executor; o desenho não depende disso
para justificar múltiplos workers agora.

**Falha/reinício de ingestão**: transação de publicação faz rollback. Draft autorizado pode
permanecer no banco com estado INTERRUPTED; nenhuma recuperação parcial. Na inicialização,
marcar operações queued/running de execução anterior como interrupted, incluindo queued com
runner_instance_id nulo (queda após commit e antes de agendar). Não restaurar a conversa;
o usuário pode solicitar retry explícito da operação autorizada.
Uma versão ativa antiga READY não é removida por falha de reindexação.

**Expiração**: ocorre em fechamento/reinício, não por navegar. Recusar novo material ao atingir
limite de RAM, sem expirar antecipadamente fontes existentes. Contratos retornam 410 para
recurso efêmero indisponível; reobter conteúdo exige novo pedido/consentimento de pesquisa.

## Consultas e índices iniciais

FKs e índices B-tree para material_id, version_id, estados e chaves idempotentes.
Busca exata pgvector cosine_distance, filtrando active_version READY e embedding_profile_id;
ordenação estável em empate por chunk_id. Sem HNSW/IVFFlat antes de medição.
Contar chunks esperados/publicados e validar em transação; filtro READY é obrigatório mesmo
quando o volume de dados é pequeno. Relatórios só exportam fixtures autorizadas.

## Migração e verificação

Alembic versiona extensão/schema; verificar privilégios de CREATE EXTENSION no setup do banco,
separados do usuário de runtime com permissões mínimas. Testar banco vazio, upgrade, rollback
transacional e incompatibilidade de dimensão com PostgreSQL real em Compose.
Mudar chunking preserva versão anterior e cria nova pipeline_version, sem reescrever citações.

Provas mínimas: golden bytes→text→spans; seleção repetida/concorrente; fechar versus selecionar;
falha no último embedding; restart antes de publish; query nunca retorna draft; marker temporário
ausente de SQL/logs/arquivos; modelos/perfis incompatíveis nunca entram na mesma comparação.
