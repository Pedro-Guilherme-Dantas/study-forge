# Ensaio visual e revisão de falhas — 2026-10-29

Ambiente visual separado: localhost:5173, um contêiner de ensaio com a mesma UI e
API da imagem do produto, schema PostgreSQL exclusivo `sf_ui_*`, chaves vazias e
provedores fixture identificados na tela. A aplicação real em :8000 e sua
biblioteca não receberam os materiais do ensaio. O harness é executado apenas por
`python -m evals.ui_rehearsal`, exige UI_REHEARSAL=1 e não é importado pelo produto.

## Observações executadas no navegador

| Cenário | Resultado observado |
|---|---|
| Biblioteca vazia | Contadores zero, busca por nome e ação Markdown visíveis. |
| Chat sem evidência | Insuficiência explícita e oferta de pesquisa. |
| Recusa da oferta | Progresso confirmou nenhuma pesquisa. |
| Pesquisa explícita | Iniciou diretamente, sem nova confirmação. |
| Pesquisa em andamento | Estado de espera visível e botão ocupado. |
| Pesquisa vazia | Mensagem específica de conclusão sem fontes, após correção. |
| Falha total | Mensagem de falha, sem alegação de fontes obtidas. |
| Falha parcial | Um cartão disponível e outro indisponível; somente o disponível oferece inspeção/seleção. |
| Seleção explícita | Inspeção → checkbox → guardar → recibo; checkbox aceito desabilitado. |
| Ingestão | Biblioteca transitou de Processando para Disponível, mantendo origem web. |
| Falha de ingestão | Material Falhou, sem trechos, com Tentar novamente. |
| Recuperação explícita | Nova tentativa concluiu; Progresso mostrou tentativa 2/publicação/concluído. |
| Seleção repetida | Biblioteca continuou com exatamente dois materiais, sem duplicação. |
| Citação | Expandiu origem Biblioteca, seção e linhas do trecho. |
| Modal/teclado | Foco inicial em fechar, Shift+Tab para último link, Tab volta ao início, Escape fecha e restaura foco na linha do material. |
| Reinício do processo | Chat limpo com aviso de reinício; biblioteca selecionada permaneceu disponível. |
| Fechamento durante trabalho | Chat limpo e foco na pergunta; fontes não reapareceram ao navegar. |
| Expiração | Aviso de descarte preservado ao abrir Fontes depois de encerrar, após correção. |
| Erro no chat | Mostra FALHA NA RESPOSTA e mensagem compreensível; campo permite outra pergunta. |
| Serviço indisponível | Após kill do contêiner isolado, aviso orienta verificar a aplicação; não aparece conclusão falsa. |
| Interrupção abrupta | Ingestão em embed foi interrompida por kill; reinício detectou operação órfã como Interrompida, sem versão consultável. |
| Recuperação após kill | Tentar novamente concluiu na tentativa 2, preservando os dois materiais anteriores. |

## Correções motivadas pelo ensaio

Pesquisa vazia antes parecia não iniciada. Falha total antes era descrita como
parcial. Esses estados agora têm mensagens distintas, sem apagar fontes anteriores
válidas. O cabeçalho de uma resposta que falhou não continua indicando consulta.
O aviso de descarte sobrevive à navegação entre telas, somente na RAM; não se
introduziu armazenamento do histórico. Três testes do cliente verificam fechamento
somente após sucesso, troca de instância e sessão expirada sem replay de mutação.

## Bloqueio e limites

Upload visual novamente recusado pela revisão automática da ferramenta do
navegador: a autorização de upload não foi concedida. Nenhum caminho alternativo
foi usado para contornar o bloqueio. T036 continua aberta. Validação de arquivo
inválido/vazio/NUL, tamanho e ingestão Markdown foi revista por pytest em schemas
isolados, e não apresentada como upload visual aprovado.

Esta rodada visual não envia chamadas reais aos provedores; as duas integrações
externas anteriores estão documentadas separadamente. Não é auditoria completa de
acessibilidade nem benchmark de qualidade semântica. Comparação de retrieval
interrompida por cota permanece fora deste ensaio e pendente.

## Regressões executadas

- 24 testes de falhas/segurança/seleção/cancelamento: aprovados em 5,72 s.
- Suíte completa da imagem: 122 aprovados, 2 externos opt-in separados, em 6,22 s.
- Cliente frontend: 3 testes aprovados com Node nativo em contêiner, sem novo framework.
- Build inclui typecheck TypeScript e Vite: aprovado após as correções.

Capturas: rehearsal-partial.png, rehearsal-ingestion-failed.png e
rehearsal-recovered.png. Os textos e URLs
mostrados são fixtures autorais; nenhuma credencial aparece nas capturas.

## Encerramento

A aba e o contêiner de ensaio foram fechados, e somente o schema sf_ui exclusivo
foi removido. Consulta posterior confirmou zero materiais em public.materials.
Aplicação principal recriada em modo real com as correções. Não houve nova chamada
Gemini/Brave nesta rodada; limites externos anteriores não foram contornados.
