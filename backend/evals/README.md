# Avaliações do StudyForge

Tudo roda em contêineres. A chave permanece no ambiente do backend; scripts não imprimem Settings,
variáveis de ambiente completas ou exceções do SDK com dados da requisição.

## Corpus

`corpus/` contém 12 artigos completos em português obtidos da web por solicitação explícita do
usuário. `corpus/manifest.json` identifica origem, revisão, hash, tamanho, autores e licença.
Veja `corpus/NOTICE.md` para atribuição CC BY-SA 4.0. O corpus sintético anterior permanece em
`corpus/synthetic/` e não representa mais o conjunto principal de avaliação.

`retrieval_cases.jsonl`: 32 perguntas com rótulos de documentos e passagens. IDs `section-*`
exigem uma seção, `multi-*` combinam documentos e `absent-*` não têm resposta no conjunto.
Os rótulos são propostas inspecionáveis, não julgamentos exaustivos de todas as passagens possíveis.

## Executar a recuperação real

```powershell
docker compose run --rm --no-deps -e APP_MODE=real -e TEST_DATABASE_URL=postgresql+psycopg://studyforge:studyforge-local@db:5432/studyforge -v "${PWD}/backend:/workspace/backend" app python -m evals.web_retrieval --dimensions 768 --chunk-targets 1600 --pause-seconds 20
```

O script usa tabelas temporárias no PostgreSQL e não escreve na biblioteca pessoal. Resultados
em `results/web-768-blocks-1600.json` incluem métricas por pergunta e os trechos recuperados,
com seção, linha, offset e similaridade, para revisão. A licença do corpus também acompanha
os excertos presentes nos resultados.

O cache `evals/.cache/authorized-web-corpus-only/` contém somente vetores desses textos selecionados
para avaliação e das perguntas autorais do benchmark. A chave inclui modelo, dimensão, tipo de
tarefa e hash do texto; não há credenciais nos arquivos. Não é cache de runtime e não pode ser
reutilizado para conversas ou fontes web não selecionadas. É ignorado pelo Git e Docker build.
Retomar uma avaliação usa a mesma captura de vetores; isso não mede variação temporal do serviço.

`--dimensions 768 1536 --chunk-targets 1600 800` amplia a comparação, com mais chamadas/custo.
O exemplo acima executa primeiro o baseline do produto; nenhum limiar de qualidade foi aprovado.

`python -m evals.run` continua sendo um ranking lexical de fixture, não Gemini. Não use seus
resultados para alegar qualidade semântica. A nova avaliação real também separa recall por
documento de cobertura da passagem: achar o artigo não garante achar a resposta.

## Gerar novamente os dados

`python -m evals.import_web_corpus` baixa revisões atuais e altera os hashes. Não execute apenas
para reproduzir uma medição existente: use os arquivos/revisões já versionados. Após alterar
fontes, revise os rótulos antes de rodar `python -m evals.label_web_cases`.

Testes externos exigem `RUN_EXTERNAL_TESTS=1`. A suíte normal limpa credenciais no próprio processo
de teste e não usa a chave real. O runner comportamental usa fixtures e registra separadamente
a necessidade de revisão semântica com respostas reais.
