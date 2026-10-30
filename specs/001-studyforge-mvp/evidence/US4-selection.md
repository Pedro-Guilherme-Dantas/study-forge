# US4 — seleção, origem e recuperação

Resultados combinados da suíte PostgreSQL isolada e do ensaio visual de
2026-10-29; testes externos anteriores continuam separados.

| Cenário | Evidência |
|---|---|
| US4-1 | Inspeção/checkbox/guardar na UI; somente selecionada entrou na biblioteca. Teste selection_retention verifica A selecionada e B temporária em todas as tabelas. |
| US4-2 | Modal com origem web e linhas do trecho; testes de promoção verificam URL/hash/grant/version. Reinício preservou material. |
| US4-3 | Seleção repetida na UI manteve dois materiais. Testes SQL confirmam mesmo grant/operação, inclusive concorrência e Idempotency-Key. |
| US4-4 | Fonte selecionada falhou em embed, sem versão/trechos disponíveis. UI ofereceu retry e concluiu na tentativa 2. Último vetor inválido é coberto por teste atômico. |
| US4-5 | Inspeção de SQL/logs/arquivos, callback rejeitado por epoch e descarte em fechamento/reinício; veja E0-retention.md e E5-promotion.md. |
| US4-6 | Contratos rejeitam snapshot diferente com 409 e fonte encerrada com 410; nada é gravado. Aviso de expiração revalidado na UI. |

Falhas controladas usam providers fixture; não simulam aprovação de Gemini/Brave.
Recuperação após kill real do contêiner também passou. Materiais de ensaio ficam
em schema exclusivo; o ensaio não depende de inserir documentos na biblioteca pessoal.
