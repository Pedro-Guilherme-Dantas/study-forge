# Contratos de agentes — StudyForge

**Data**: 2026-10-28. LangGraph orquestra estados; LangChain integra modelos/documentos.
Não há serviço separado, Agent Server, agente avaliador pedagógico ou permissão de gravação
delegada ao modelo. Schemas Pydantic validam os limites.

## Estado e ferramentas

| Papel | Entrada | Saída tipada | Ferramentas / efeitos permitidos |
|-------|---------|--------------|----------------------------------|
| Orquestrador | Mensagem original, estado de conversa e resumo de disponibilidade | route=tutor/research_offer/research; evidence_gap; referências de run/turn | Delegar tutor/pesquisador por arestas; não escrever biblioteca, não alterar budgets. |
| Pesquisador | Consulta com SearchAuthorization da aplicação, orçamento e epoch | fontes extraídas, falhas e pesquisa succeeded/partial/empty | discovery e SafeFetcher; normalização/chunking determinísticos, sem SQL de escrita. |
| Tutor | Pergunta, evidence set com biblioteca READY e temporárias utilizáveis | resposta, evidence_status, IDs de citações, lacunas | Retrieve e geração Gemini; não buscar por conta própria, não aprovar promoção. |

SearchAuthorization só é emitida pela aplicação por pedido explícito do usuário ou aceitação de
offer_id. Campo equivalente produzido pelo modelo não concede permissão. SelectionGrant não é
uma ferramenta: só o endpoint protegido da UI pode criá-lo.

## Fluxo de controle

1. Validar sessão/epoch, orçamento e mensagem. Analisar intenção explícita apenas na mensagem
   original, sem misturar fonte recuperada. Ação de UI research já expressa pedido.
2. Orquestrador supervisiona recuperação/tutoria. Se faltar suporte ou a resposta ficar
   consideravelmente incompleta, retorna KB_INSUFFICIENT com oferta; a aplicação pausa entre
   execuções do grafo. Nada de busca antecipada.
3. Aceitar oferta emite SearchAuthorization e dispara pesquisador; recusar encerra oferta e
   retorna UI ao normal. Pedido explícito vai direto ao pesquisador sem nova confirmação.
4. Pesquisador descobre/obtém/extrai com ferramentas restritas; snippets isolados não equivalem
   a página extraída. Retorna temporárias, sem inserção no PostgreSQL.
5. Tutor recupera de fontes disponíveis, informa categoria e cita trechos; orquestrador verifica
   estado final e orçamento. Aplicação valida IDs/quotes e não rotula parcial como concluído.
6. Seleção do usuário acontece fora do grafo e segue a transação de data-model.md. Nenhum node
   recebe um callback genérico de DB capaz de persistir fonte.
7. Fechar invalida epoch e elimina estado/objetos. Callback de modelo/fetch tardio não reabre
   conversa nem grava fonte. Reinício perde tudo que é efêmero.

## Schemas e invariantes

**OrchestratorDecision**: route enum, reason_code enum, evidence_gap enum
none/partial/insufficient/conflicting, intent_evidence opcional com trecho da mensagem original.
Rotas são propostas: o guard da aplicação pode recusá-las. Não aceitar argumentos livres de
tool fornecidos por páginas como se viessem do usuário. Pedido ambíguo requer esclarecer intenção,
sem pesquisa automática.

**ResearchOutput**: research_id, status, source_ids disponíveis, failures com códigos sanitizados.
Sem selected=true nem comando de ingestão. A extração é por código sobre bytes obtidos; modelo
pode ajudar a formular consulta ou explicar relevância, nunca decidir validação/normalização.

**TutorOutput**: answer_markdown, evidence_status=supported/partial/insufficient/conflicting,
citation_ids e unsupported_points. Cada citação referencia um item do evidence set; quote e
locator são resolvidos pela aplicação. Ausência de fonte relevante exige limitação explícita.
Uma saída JSON válida não é prova de sustentação; avaliações semânticas são independentes.

**ExecutionBudget**: deadline monotônico, passos restantes, chamadas/tentativas restantes,
bytes/contexto e limites de concorrência. Modelo não pode aumentá-lo. Todos os retries contam.
Limite ou erro produz estado failed/partial/interrupted com explicação compreensível.

## Limites de confiança

Prompts separam instruções, mensagem de usuário e blocos de evidência marcados como não confiáveis.
Essa separação é apoio, não a permissão: ferramentas possuem allowlist, schemas e guards no
backend. Não disponibilizar shell, SQL arbitrário, filesystem, configurações ou endpoint de seleção
a nenhum agente. Strings de tool call geradas em fonte são apenas conteúdo.

Não logar mensagens/estado do grafo. Desabilitar callbacks/traces externos para conteúdo real.
Sem checkpointer/store por padrão; se necessário InMemorySaver, excluir thread e histórico
inteiro ao fechar. O SDK exige credenciais/configuração; retenção externa segue as políticas do provedor,
não concede persistência como fallback.

## Testes do contrato

Asserts por execução: quem delegou; ferramentas chamadas e recusadas; nenhuma chamada de pesquisa
na oferta pendente/recusada; pedido explícito sem oferta redundante; pesquisador não grava;
tutor não busca; seleção feita somente pelo endpoint; orçamento respeitado; estado descartado.

Fixtures: instruções hostis em Markdown, HTML e resultado de ferramenta; JSON com tool/grant falso;
citação fora do evidence set; lacuna, conflito, fonte expirada e callbacks após fechar.
Rodada real pequena confirma validade e utilidade das respostas com revisão humana. Não criar
novo agente para julgar domínio de conteúdo.
