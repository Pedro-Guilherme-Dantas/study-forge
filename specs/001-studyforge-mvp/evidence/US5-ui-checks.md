# Inspeção visual local — 2026-10-29

## Revisão posterior

Novo ensaio isolado executado: consulte rehearsal.md e US5-navigation.md para a
matriz atual, incluindo falha parcial/total, recuperação, interrupção abrupta,
expiração e teclado. O harness backend/evals/ui_rehearsal.py prepara esses estados
sem adicionar endpoints de teste ao produto. Upload visual continua recusado pela
revisão automática do navegador; não foi contornado.

## Histórico inicial

Navegador em http://127.0.0.1:8000, modo fixture sem chamadas externas.

| Verificação | Observação |
|---|---|
| Biblioteca vazia | Identificação, contadores reais e ação de Markdown presentes. |
| Chat sem evidência | Resposta de insuficiência, sem referência inventada, e oferta visível. |
| Recusar | Oferta removida, retorno ao chat normal. Sem pesquisa registrada. |
| Pedido explícito | Pesquisa iniciada sem confirmação redundante. |
| Navegar para fontes | Dois snapshots sintéticos disponíveis, com título/endereço/prévia e identificação temporária. |
| Progresso | Pesquisa concluída, sem notas ou domínio de conteúdo. |
| Retornar ao chat | Mensagens e referência temporária preservadas ao navegar. |
| Encerrar | Chat vazio e foco no campo de pergunta. |
| Fontes após encerrar | Nenhuma fonte disponível; sem restauração silenciosa. |

O ensaio visual não guardou fontes. Consulta SQL posterior confirmou zero materiais na biblioteca pessoal. Upload pelo navegador foi rejeitado pela política da ferramenta e não foi contornado; testes HTTP verificaram o fluxo em schemas isolados. Ensaio visual de upload e matriz completa com erro/partial/expiração preparados ainda pendentes. Foco/teclado foram implementados, mas ainda não há afirmação de auditoria completa de acessibilidade.
