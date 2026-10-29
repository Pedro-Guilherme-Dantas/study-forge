# HTTP API e interface — contrato proposto

**Versão**: 0.1.0 de desenho, 2026-10-28. API executada no monólito em localhost.
[openapi.json](openapi.json) descreve rotas e esquemas; divergência deve ser corrigida antes
da implementação. Exemplos representam contratos futuros, não endpoints já executáveis.

## Regras comuns

Base `/api`, JSON UTF-8, UUIDs opacos e enums compartilhados com TypeScript/Pydantic.
Timestamps UTC ISO-8601. Sem chaves do provedor no cliente, URL arbitrária de fetch ou tools
de ingestão expostas ao modelo. Perfil/modelo/limites são configurados no backend.

Sessão por cookie HttpOnly SameSite=Strict e CSRF em toda mutação; Host/Origin permitidos são
loopback exato, não curingas. Cookie apenas identifica a pessoa local já no navegador; sem
login/cadastro ou exposição pública. Vite usa proxy no desenvolvimento e build demo é same-origin.
O cookie pode sobreviver no browser como ID opaco, mas o servidor não restaura contexto após boot.
Resposta 410 manda limpar estado e criar nova sessão/conversa; não reenviar pergunta automaticamente.

Respostas de conteúdo e estado usam Cache-Control: no-store. Não colocar mensagens, URLs de fontes
ou pesquisas em query string; logs de acesso omitem query. Não persistir respostas em storage do
navegador. Polling de estado usa IDs, cessa em estado terminal e ao fechar a conversa.
Baseline 1,5 s entre polls para o ensaio, ajustável em E5.

Erro:
```json
{
  "error": {
    "code": "SOURCE_EXPIRED",
    "message": "Esta fonte não está mais disponível. Inicie uma nova pesquisa para obtê-la.",
    "stage": "selection",
    "retryable": false,
    "request_id": "identificador-aleatorio"
  }
}
```

Códigos: INVALID_MARKDOWN/422, PAYLOAD_TOO_LARGE/413, SESSION_EXPIRED/410,
CONVERSATION_CLOSED/410, SOURCE_EXPIRED/410, SNAPSHOT_MISMATCH/409, OPERATION_BUSY/409,
DESTINATION_BLOCKED/422, EXECUTION_LIMIT/429, EXTERNAL_UNAVAILABLE/502,
PROVIDER_NOT_CONFIGURED/503, INGESTION_FAILED/500.
Mensagem sanitizada, nunca stacktrace, prompt, corpo HTTP ou segredo. retryable não executa
automaticamente retry de promoção; a UI oferece ação explícita quando o contrato permite.

## Rotas

| Método / rota | Entrada e saída | Efeito / estado |
|---------------|-----------------|----------------|
| GET /api/runtime | RuntimeInfo | Config pública, server_instance_id, gate de provedor e avisos; não testa API externa automaticamente. |
| POST /api/sessions | SessionReceipt + Set-Cookie | Cria sessão efêmera e CSRF; não cria usuário no banco. |
| POST /api/conversations | ConversationReceipt | Cria conversa vazia da sessão. |
| DELETE /api/conversations/{conversation_id} | 204 | Fecha, invalida epoch, cancela/descarta objetos. Repetição sem conteúdo é no-op se sessão válida. UI cria conversa nova vazia. |
| POST /api/conversations/{conversation_id}/turns | TurnRequest → 202 TurnReceipt | Inicia um turno limitado; intent=research é ação explícita. Mensagem explicitamente pedindo pesquisa também não exige confirmação. |
| GET /api/conversations/{conversation_id}/turns/{turn_id} | TurnResult | running, awaiting_research_consent, complete, partial, insufficient ou failed; inclui oferta/citações quando aplicável. |
| POST /api/conversations/{conversation_id}/research-offers/{offer_id}/decision | accept → OfferDecision | Recusa: 200 declined sem pesquisa. Aceitação: 202 accepted com research_id; repetição reutiliza o resultado. |
| POST /api/conversations/{conversation_id}/research | topic → 202 ResearchReceipt | Pedido explícito pela UI; execução supervisionada, sem segunda confirmação. |
| GET /api/conversations/{conversation_id}/research/{research_id} | ResearchResult | running, succeeded, partial, empty, failed ou interrupted, fontes e falhas sanitizadas. |
| GET /api/conversations/{conversation_id}/sources/{source_id} | TemporarySourceDetail | Snapshot e locators somente da conversa ainda aberta. Não coleta URL de novo. |
| POST /api/conversations/{conversation_id}/sources/{source_id}/selection | snapshot_hash → PromotionReceipt | 202 nova ingestão; 200 se já aceita. Só esta ação do usuário autoriza persistência web. |
| GET /api/conversations/{conversation_id}/citations/{citation_id} | CitationDetail | Verifica vínculo ao turno e disponibilidade; fonte temporária expirada → 410. |
| POST /api/materials | multipart Markdown → 202 IngestionReceipt | Intenção de ingestão local, validação e tamanho antes de processamento; arquivo rejeitado não aparece READY. |
| GET /api/materials | MaterialSummary[] | Biblioteca com estados e versão ativa, paginação simples por cursor. |
| GET /api/materials/{material_id} | MaterialDetail | Origem, versões e operação; não muda conteúdo. |
| GET /api/materials/{material_id}/versions/{version_id}/chunks/{chunk_id} | LibraryChunk | Texto/locator da versão READY; respeita associação dos IDs. |
| GET /api/operations/{operation_id} | IngestionReceipt | Estado durável de operação autorizada, independente da conversa. |
| POST /api/operations/{operation_id}/retry | 202 IngestionReceipt | Só FAILED/INTERRUPTED autorizado; mesma operação lógica e versão; limite de tentativas explícito. |
| GET /api/progress | ProgressSnapshot | Biblioteca/ingestões duráveis + pesquisa da conversa atual na RAM. Sem histórico pedagógico. |
| GET /health/live e /health/ready | HealthInfo | Processo e DB/migração; não expõe credenciais nem faz pesquisa ou modelo como efeito colateral. |

O header opcional Idempotency-Key identifica ação do cliente mas nunca autoriza conteúdo.
A chave idempotente de domínio inclui origem, snapshot, pipeline e perfil. Chave reutilizada
com corpo diferente retorna 409. Para seleção, mesmo conteúdo/hash retorna recibo original;
fechamento antes da aceitação retorna 410. Uma aceitação já commitada é operação de biblioteca
consultável em /operations mesmo que a conversa tenha sido fechada.

## Mensagens, autorização e promoção

```json
{
  "message": "Pesquise sobre ciclos biogeoquímicos",
  "intent": "auto"
}
```

Mensagem explícita é reconhecida sem confirmação adicional. Para necessidade detectada pelo
sistema, retornar oferta com offer_id, turn_id e reason_code=KB_INSUFFICIENT; aceitar via rota
de decisão é distinto de seleção de fontes. Não permitir que um texto citado ou saída de ferramenta
seja usado como evidência de intenção explícita do usuário.

```json
{
  "snapshot_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
```

O corpo de seleção não aceita text, url, selected=true produzido por agente ou SQL. A aplicação
resolve o ID efêmero no estado da sessão e verifica hash/epoch antes de criar SelectionGrant.

## Citações

Uma resposta estruturada contém answer_markdown, evidence_status e citations. Cada afirmação
fundamentada referencia um ID fornecido pelo backend. Biblioteca: material_id, version_id,
chunk_id, nome, locator e quote. Temporária: source_id, snapshot_hash, URL, identificação,
locator no snapshot extraído, quote e disponibilidade temporária.

Exemplo resumido:
```json
{
  "status": "complete",
  "evidence_status": "supported",
  "answer_markdown": "A explicação é sustentada pelo trecho [c1].",
  "citations": [{
    "citation_id": "c1",
    "scope": "temporary",
    "source_id": "uuid-da-fonte",
    "snapshot_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "title": "Ciclo da água",
    "origin_url": "https://example.org/ciclo",
    "quote": "Trecho realmente presente no snapshot.",
    "locator": {
      "kind": "html_extracted_snapshot",
      "section_path": ["Ciclo da água"],
      "start_char": 10,
      "end_char": 53,
      "start_line": 2,
      "end_line": 3,
      "offset_unit": "unicode_code_point"
    }
  }]
}
```

IDs/quotes são resolvidos e validados no evidence set do turno. O modelo não escolhe URL livre.
Se a referência é inválida, tentar correção de esquema uma vez dentro do orçamento; caso não
resolva, resposta falha/parcial/insuficiente explícita. Validação estrutural não substitui o teste
de sustentação semântica. Ao fechar, toda referência de conversa é descartada, mesmo da biblioteca;
os chunks autorizados continuam consultáveis pela biblioteca.

## Navegação e estados

Quatro destinos React: chat, biblioteca, progresso e seleção de fontes. Usar estado comum
efêmero para sessão/conversa e polling; navegar preserva fontes até encerramento/reinício.
Não adicionar painel de notas, histórico persistente, quizzes ou configurações multiusuário.

- **Chat**: estado vazio, aguardando resposta, oferta de busca, recusa retornando ao normal,
  resposta fundamentada/parcial/insuficiente, erro e conversa expirada. Botão Encerrar conversa
  faz DELETE, limpa todos os buffers do cliente e cria chat vazio.
- **Biblioteca**: vazio com upload Markdown; lista com processing/ready/failed/interrupted;
  detalhe e referência consultável; erro de upload/ingestão e ação retry quando permitida.
- **Fontes**: carregamento de pesquisa, nenhum resultado utilizável, resultados parciais,
  cartões temporários inspecionáveis, indisponível/expirada, seleção em processamento/já aceita.
  Seleção de vários cartões chama apenas os IDs marcados, com resultados independentes visíveis.
- **Progresso**: estados operacionais de materiais e pesquisas/ingestões da conversa atual.
  Nenhum percentual ou ETA é inventado, nenhum status parcial é exibido como concluído.

Citações abrem painel com categoria biblioteca/temporária, identificação, data de obtenção,
snapshot/versão e passagem. Abrir link remoto é ação explícita do usuário; app não carrega
imagens/iframes remotos automaticamente. Expiração limpa fontes; aviso genérico não preserva
cópia do conteúdo descartado. Novo server_instance_id limpa todos os dados efêmeros do cliente.

Acessibilidade de base: navegação por teclado, foco após erro/encerramento, labels nos inputs,
estados textuais além de cor e região de status anunciável. Não criar requisito numérico de
acessibilidade não discutido; validar esses fluxos no ensaio.

## Informação sobre provedores

Aviso visível no chat/upload/fontes: perguntas e trechos necessários podem ser enviados à
API Gemini para geração/embeddings; a consulta de busca vai ao provedor de descoberta.
Informar modelo/provedor configurado, retenção verificada ou gate bloqueado e escopo enviado.
As chaves ficam no backend. Não apresentar execução como integralmente local nem
consentimento de pesquisa como seleção para guardar. Sem modal adicional em todo pedido explícito.

## Verificações de contrato

Pytest valida OpenAPI/Pydantic, códigos e estados, ausência de efeitos na recusa, CSRF/Origin,
IDs da própria sessão, invalidação após fechar/reiniciar, seleção idempotente e hashes diferentes.
Teste negativo injeta marker em título, URL, corpo e erro de fonte não selecionada; nenhum marker
pode ir ao SQL/log/arquivo. Build TypeScript e cliente devem usar os mesmos enums; mudanças de
contrato alteram API/schema e testes na mesma revisão.

## Refinamento durante a implementação

GET `/api/materials/{material_id}/versions/{version_id}/chunks` retorna `{items: LibraryChunk[]}`
(até 2.048 trechos, limite finito do chunker). Foi acrescentado para a biblioteca descobrir as
passagens da versão disponível sem conhecer antecipadamente os IDs dos chunks. Aplica os mesmos
controles de associação e READY da consulta individual. Não altera autorização ou persistência.
O contrato OpenAPI inclui essa operação como `listLibraryChunks`.
