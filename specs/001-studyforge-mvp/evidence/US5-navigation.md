# US5 — navegação e ciclo de vida

Verificado no ensaio visual de 2026-10-29, detalhado em rehearsal.md.

- US5-1: os quatro destinos foram acessados pela navegação.
- US5-2: vazio, consulta em andamento e processamento foram observados antes da conclusão.
- US5-3: pesquisa vazia, falha parcial, erro total e expiração foram observados;
  mensagens imprecisas foram corrigidas e revalidadas.
- US5-4: progresso mostrou publicação, falha/interrupção e número da tentativa,
  sem inventar percentuais ou medição de aprendizagem.
- US5-5: processo reiniciado com schema preservado; chat descartado e biblioteca
  selecionada conservada. Interrupção abrupta também recuperou o estado órfão.
- US5-6: encerrar limpou chat/fontes e restaurou foco; biblioteca permaneceu.

Teclado no modal verificado por Tab, Shift+Tab e Escape, com restauração de foco.
Os testes nativos do cliente cobrem descarte somente após confirmação do backend,
troca de instância e sessão expirada sem replay de mutações. Não é uma auditoria
integral de acessibilidade. Upload visual segue bloqueado pela ferramenta e é
documentado separadamente, sem marcar US1 como inteiramente ensaiada.
