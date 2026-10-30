# US1 — biblioteca local

Execução em contêiner, PostgreSQL/pgvector real e embeddings de fixture, sem chamadas externas.
A suíte completa após a correção de isolamento passou com **35 testes**; após adicionar os
contratos iniciais do tutor passou com **44 testes**. O build de produção inclui typecheck e Vite.

Verificados: rejeição de inválidos/tamanho, MIME enganoso sem confiar no MIME, consulta de
passagens/locators, associação material-versão-chunk, repetição concorrente, publicação atômica,
falha no vetor final, retry antigo sem regressão, falha de agendamento com recuperação e biblioteca
persistente entre instâncias da aplicação. Migração 0001 aplicada ao banco local; runtime usa
papel sem superusuário. DDL da migração está congelado para não acompanhar alterações futuras do ORM.

Inspeção visual: página servida em 127.0.0.1:8000, navegação, estado vazio e aviso fixture.
O upload pelo navegador foi recusado pela política da ferramenta e não foi contornado.
O caminho HTTP de upload foi verificado em schemas de teste, não como ensaio visual completo.

Ocorrência corrigida: depois de criar tabelas em public, create_all(checkfirst=True) nos testes
encontrava essas tabelas por search_path e não criava tabelas isoladas. Agora checkfirst=False
cria todas no schema aleatório e verifica a quantidade de tabelas. TEST_DATABASE_URL é obrigatório.
Seis materiais sintéticos daquela execução foram removidos por seus UUIDs exatos; nenhum dado de
usuário foi removido. Biblioteca local voltou a zero materiais. O teste posterior passou isolado.

Parâmetros de chunking/perfil continuam experimentais. Esta fatia não equivale ao MVP completo.
