# E5 — promoção e publicação

Executado em PostgreSQL/pgvector real, em schemas descartáveis, na suíte de
2026-10-29: 121 testes aprovados e 2 integrações externas opt-in ignoradas.

- `test_promotion_races.py`: seleção concorrente com um único grant/operação,
  fechamento antes da seleção sem escrita, fechamento após commit com conclusão,
  falha entre commit e agendamento e recuperação explícita sem a conversa.
- `test_selection_sql_barrier.py`: uma transação segura o advisory lock 72198341;
  a seleção entra no lock da conversa e o fechamento aguarda. Liberar a transação
  permite commit e descarte, seguido de ingestão concluída e exatamente um grant.
- `test_ingestion_publication.py`: último vetor inválido sem chunks publicados,
  capacidade liberada na falha, upload concorrente, retry antigo sem regressão da
  versão ativa e operações queued/running órfãs marcadas como interrompidas.
- `test_selection_retention.py`: seleciona A, usa B temporariamente no tutor e
  inspeciona todas as tabelas, logs capturados e locais graváveis do contêiner;
  nenhum marcador de B é encontrado. Fechamento remove mensagens/fontes/citações.
- `test_full_journey.py`: nova instância da aplicação conserva os dois materiais
  autorizados e não restaura pesquisa/chat.

As contagens e estados SQL são asserções executadas, não consultas planejadas.
Não foram usados documentos pessoais. A integração externa separada também
comprovou seleção seguida de fechamento e ingestão real com Gemini.
