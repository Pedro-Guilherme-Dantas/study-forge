# Captura detalhada LangSmith — 2026-10-30

Solicitação explícita do usuário: inspecionar perguntas, respostas e execução real pela interface
e pelo LangSmith. Modo de metadados continua padrão; captura detalhada é opt-in por
`STUDYFORGE_TRACE_CONTENT=true`, dependente de `STUDYFORGE_TRACING=true` e chave configurada.
As duas flags foram habilitadas no `.env` local sem exibir ou alterar credenciais.

## Conteúdo e limites

- Turno: pergunta, intenção, resposta final, lacunas e citações.
- Recuperação: pergunta, textos selecionados, título, origem, localizador, ID de evidência e distância.
- Tutor: pergunta, evidências e saída estruturada; não confundir classificação com correção comprovada.
- Geração: prompt enviado como mensagem, resposta textual bruta e contagens de tokens disponíveis.
- Pesquisa: consulta e resumos de fontes; vetores não são exportados. Embeddings de documentos
  capturam amostra de um texto por chamada, sem consumir todo o orçamento com páginas completas.
- Campos de credencial e valores das três chaves configuradas são mascarados. Não é anonimização
  geral; não se serializam settings, callbacks, orçamento, headers ou exceções SDK.
- Até 32 KiB por string, orçamento textual de 256 KiB por árvore, profundidade seis, até 20 itens
  por lista e 40 campos por objeto. Truncamentos são sinalizados; não se promete conteúdo ilimitado.
- Fila/exportação continuam limitadas e somente em RAM. Logs locais e SQL não recebem os payloads.
  Retenção externa segue o LangSmith; fechar conversa não apaga traces remotos. Aviso na UI atualizado.
- Endpoint de diagnóstico inclui modo e último código de falha sanitizado.

## Validação executada em containers

- Suíte completa: **142 passed, 2 skipped, 18 warnings**. Skips são Gemini/web externos opt-in;
  warnings são depreciações transitivas. Verifica metadados sem conteúdo, captura detalhada,
  mascaramento, truncamento, objetos não serializáveis, falhas e contratos/aviso externo.
- Ensaio detalhado de fixtures: **cinco árvores exportadas, zero falhas ou descartes**.
- Jornada HTTP real em schema PostgreSQL isolado: upload Markdown autoral → embeddings Gemini →
  recuperação → tutor Gemini → citações → encerramento: **um teste externo aprovado, 7,49 s**.
  Aguardou drenagem do exportador antes de fechar o servidor de teste. Biblioteca pessoal preservada.
- Consulta remota confirmou **seis roots detalhados indexados** e na árvore real inputs e outputs
  em turno, recuperação, tutor e geração, com prompt, resposta bruta e documentos disponíveis.
- Build/typecheck em `docker compose build --quiet app` aprovado. Configuração local recriada.
- Uma consulta extra à API de leitura recebeu `429 Rate limit exceeded`. O processo local também
  registrou uma falha de exportação cuja causa não havia sido retida. Acrescentado diagnóstico
  sanitizado para novas falhas: `EXPORT_RATE_LIMITED`, `EXPORT_AUTH_FAILED`, `EXPORT_TIMEOUT`
  ou `EXPORT_FAILED`. Não foram feitas tentativas repetidas de leitura após o 429.

Árvore real verificada: `50d24c20-4d74-452e-900a-ae98197d4a44`, com conteúdo autoral de teste.
Verificação foi por API, sem afirmar inspeção visual da interface remota.
Traces antigos não são preenchidos retroativamente. Sem stage ou commit neste incremento.
