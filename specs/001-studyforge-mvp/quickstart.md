# Executar e verificar StudyForge

Observabilidade opcional implementada: consulte [o guia LangSmith](../../docs/observabilidade-langsmith.md)
para configuração, cenários de ensaio e interpretação das execuções. A integração usa spans
explícitos, com metadados por padrão e conteúdo autorizado via `STUDYFORGE_TRACE_CONTENT=true`;
não habilite as flags de captura automática LangSmith/LangChain. O guia mostra o teste manual.

Os fluxos locais estão implementados. Os comandos abaixo foram executados em
contêineres. As jornadas reais Gemini/Brave já passaram separadamente; avaliações
de recuperação e itens de aceite ainda abertos estão em evidence/readiness.md.

## Ambiente local com fixtures

Requer Docker Desktop/Engine com Compose e navegador no host. Não instalar Python, Node ou dependências no host. Na raiz do repositório:

```powershell
docker compose build app
docker compose up -d db
docker compose run --rm --no-deps -e DATABASE_URL=postgresql+psycopg://studyforge:studyforge-local@db:5432/studyforge app alembic upgrade head
docker compose up -d app
docker compose ps
```

A migração usa o papel administrativo somente nesse comando. O serviço app usa studyforge_runtime sem superusuário; PostgreSQL não publica porta no host. Passwords do Compose pertencem exclusivamente ao laboratório local. O script backend/db-init/001-runtime.sql cria a extensão e o papel runtime em volumes novos. Volumes anteriores a esse script precisam de sua execução administrativa explícita antes de migrar; não apagar o volume para corrigir permissões.

Abra [StudyForge local](http://127.0.0.1:8000). O banner identifica o modo de ensaio.

- Biblioteca: Markdown UTF-8 até 1 MiB; estados de processamento, trechos e locators.
- Chat: referências consultáveis e lacunas claras. Recusar oferta não pesquisa; pedir explicitamente pesquisa na web não exige confirmação adicional.
- Fontes: HTML sintético no modo fixture; inspeção e seleção explícita antes de guardar.
- Progresso: estados operacionais, sem notas ou medição de domínio do conteúdo.

O tutor extrativo e os vetores por hash verificam o fluxo, não qualidade semântica. URLs example.org/studyforge-fixture/* são identificadores de teste, não páginas realmente coletadas.

## Testes e baseline local

```powershell
docker compose run --rm --no-deps -e TEST_DATABASE_URL=postgresql+psycopg://studyforge:studyforge-local@db:5432/studyforge app pytest -q -p no:cacheprovider
docker compose run --rm --no-deps app python -m evals.run
```

Os testes criam schemas aleatórios e removem somente os próprios schemas. TEST_DATABASE_URL é obrigatório para PostgreSQL; sem ele esses casos são skipped e não contam como integração aprovada. O runner usa corpus próprio de 12 documentos/perguntas e calcula Recall@3/5/8 e MRR nos casos respondíveis; ausência de evidência é separada. Baseline fixture não é avaliação Gemini nem meta de qualidade aprovada.

O build executa typecheck TypeScript e Vite. Testes HTTP verificam destinos, DNS, IP fixado, Host/SNI e validação TLS com streams controlados; não equivalem a coleta externa real.

Regressões do cliente para encerramento, troca de instância e sessão expirada,
sem repetir automaticamente mutações (Node nativo, sem novo framework):

```powershell
docker run --rm -v "${PWD}/frontend:/web:ro" -w /web node:24-bookworm-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c node --experimental-transform-types --test tests/api.test.mjs
```

Na revisão progressiva: 6 testes aprovados. O Node informa que a transformação de tipos
é experimental; o build de produção continua usando TypeScript/Vite normalmente.

## Retenção e recuperação

Navegar preserva conversa e fontes. Encerrar descarta mensagens, fontes e citações da conversa e abre chat vazio. Reinício perde RAM e mantém biblioteca. Seleção aceita antes de fechar pode concluir ingestão; fechamento anterior recusa seleção. Operações órfãs ficam interrompidas e podem ser repetidas explicitamente, até três tentativas. Chunks parciais não ficam disponíveis. Retry de versão antiga não substitui versão ativa mais nova.

Para parar mantendo biblioteca:

```powershell
docker compose down
```

Não usar down -v no fluxo normal: apagaria o volume. Logs de corpo e captura automática de traces ficam desativados; spans operacionais externos são opcionais via `STUDYFORGE_TRACING`. Erros públicos são sanitizados e operações consultáveis. Não existe restauração de chat ou replay automático de perguntas.

## Integrações externas

Configure credenciais no backend para usar as APIs reais. O usuário retirou a exigência de comprovar retenção zero externa em 2026-10-29; o gate G0 não existe mais. A garantia de descarte é local. A interface informa que perguntas/trechos e consultas são enviados aos provedores, que aplicam suas próprias políticas.

O modelo principal é gemini-3.5-flash-lite, conforme orientação do usuário. Não há
fallback automático para 3.1; ele só deve ser considerado se limites de uso
exigirem. Dimensão 768, top-k 5, chunking e limites continuam experimentais.
O coletor solicita HTML sem compactação e rejeita codificações comprimidas;
não refaz DNS por fallback. Gemini permite no máximo duas tentativas por chamada
para erros transitórios, respeitando o orçamento compartilhado e RetryInfo.
Brave/coleta não fazem retentativas automáticas.

Para usar os serviços reais, configure APP_MODE=real no .env, além das duas chaves
no backend, e recrie o app com `docker compose up -d app`. O modo fixture continua
disponível para ensaios. Não cole chaves em comandos ou no chat.

Integrações externas opt-in (schema de teste isolado; podem consumir cota):

```powershell
docker compose run --rm --no-deps -e RUN_EXTERNAL_TESTS=1 -e TEST_DATABASE_URL=postgresql+psycopg://studyforge:studyforge-local@db:5432/studyforge app pytest -q -p no:cacheprovider tests/integration/test_gemini_external.py tests/integration/test_web_external.py
```

Ambas passaram com Gemini 3.5 Flash Lite em 2026-10-29; a segunda também usou
Brave e HTML real. Isso não substitui a avaliação semântica nem o ensaio visual.

Avaliação determinística de comportamento (também em contêiner, sem modelo real):

```powershell
docker compose run --rm --no-deps -e TEST_DATABASE_URL=postgresql+psycopg://studyforge:studyforge-local@db:5432/studyforge app python -m evals.agents
```

## Corpus representativo para avaliação

Os 12 textos sintéticos curtos foram preservados em backend/evals/corpus/synthetic. O corpus principal agora contém 12 artigos completos da web, com atribuição/licença e revisões no manifesto, além de 32 perguntas. Consulte backend/evals/README.md e evidence/E3-web-corpus.md para comandos, rótulos, métricas e revisão dos erros. Esse conjunto de avaliação é separado da biblioteca pessoal.

O runner externo de embeddings pode retomar seu cache exclusivo do corpus autorizado; esse cache não é usado pela aplicação nem incluído no Git/build. Respeite as pausas e limites da conta. A avaliação longa encontrou timeout, 429 e desconexão antes de concluir o baseline; esses eventos foram registrados e não apresentados como métricas de recuperação válidas.
