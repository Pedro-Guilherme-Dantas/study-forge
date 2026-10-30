# Estado atual — 2026-10-29

Esta seção substitui o estado das atualizações históricas abaixo.

**Condição operacional posterior:** diagnóstico após relato de uso confirmou
esgotamento da cota diária gratuita de embeddings (429). Uploads e pesquisas que
precisam de vetores reais permanecem dependentes de liberação dessa cota. Mensagem
específica e recuperação vazia sem chamada vetorial corrigidas; 130 testes
aprovados e 2 externos opt-in separados. Veja provider-quota.md. Readiness do banco
não comprova disponibilidade dos provedores externos.

- Aplicação recriada em **modo real**, Gemini **3.5 Flash Lite**, Brave configurado,
  readiness OK em http://127.0.0.1:8000. Somente APP_MODE foi alterado no .env;
  valores de credenciais não foram exibidos. Nenhum fallback 3.1 foi adicionado.
- Build/typecheck em contêiner aprovado. Revisão progressiva: **125 aprovados, 2 testes
  externos opt-in separados**. Runner de 12 casos comportamentais: 17 asserts
  aprovados com fixtures; não confundir com avaliação semântica.
- Integração real Markdown → embeddings → pgvector → Gemini/citação aprovada com
  3.5 Flash Lite (27,24 s). Integração Brave → HTML → tutor temporário → seleção
  → encerramento → ingestão aprovada (47,96 s), em schema isolado.
- OpenAPI documenta autenticação, multipart, idempotência e erros sanitizados;
  constraints aninhadas e tipos discriminados de citação foram conferidos.
- Teste SQL de barreira confirma seleção antes do fechamento. Regressões cobrem
  SSRF, gzip, orçamento, publicação atômica, autorização fora do grafo e retenção.
- Corpus real: 12 artigos, 512.403 caracteres. Baseline 768/1600 concluído;
  comparação 768/800 interrompida por 429, sem score válido. 1536 longo pendente.
- Avaliação do tutor encontrou classificação conservadora; prompt/schema foram
  ajustados. Nova rodada tem acertos e uma indisponibilidade 503 registrada;
  resultado final: 9 respostas concluídas com estados/citações corretos e 1 falha
  503 em 10 chamadas. E2/E6 registram os dados, sem alegar confiabilidade geral.

Pendências efetivas: concluir comparação de retrieval após liberação da cota,
consolidar parâmetros e completar as verificações transversais ainda abertas em
tasks.md. O ensaio visual/falhas foi executado em ambiente isolado e está em
rehearsal.md: vazio/espera, pesquisa vazia/parcial/erro, seleção repetida,
ingestão com falha, retry, cancelamento, reinício e interrupção abrupta passaram.
Corrigidas mensagens de pesquisa, cabeçalho de erro do chat e aviso de descarte.
Teclado/foco do modal verificados; não se declara auditoria completa de acessibilidade.

**Upload visual permanece bloqueado**: nova tentativa foi recusada pela revisão
automática do navegador e não foi contornada. Testes HTTP não substituem esse
ensaio. Portanto, não declarar toda a matriz de aceite ou apresentação integral
pronta. T077/T079/T084 foram concluídas; T036/T093 permanecem abertas com a ressalva.

Validação atual da revisão progressiva: 125 testes pytest aprovados (2 externos opt-in separados),
6 testes do cliente com Node nativo aprovados e build/typecheck aprovado em
contêiner. Ambiente de ensaio e schema removidos após a execução. Biblioteca
pessoal permaneceu com zero materiais. Aplicação real em :8000 recebeu as correções.

Revisão por etapas e organização das pastas registradas em
docs/revisao-progressiva.md; guia didático em docs/guia-do-projeto.md. A revisão
corrigiu a repetição de seleção com executor cheio, respostas antigas no cliente,
dependência direta de regex e default do runner de modelos. Migrações foram
testadas em schema isolado com upgrade/downgrade/upgrade. As contagens abaixo
descrevem execuções históricas e não substituem a rodada atual.

Revisão visual posterior confirmou biblioteca vazia, progresso operacional vazio,
fontes vazias e aviso de retenção/envio externo em modo real. Corrigido o texto de
fixture na tela Fontes para aparecer somente nesse modo; build/typecheck aprovado
novamente. Captura em real-sources.png. Não houve upload ou gravação na biblioteca.

## Histórico da implementação local

## Entregue e executado

- Docker Compose, imagens por digest, locks Python/Node, build TypeScript/Vite e PostgreSQL/pgvector real.
- Biblioteca Markdown com pipeline determinístico, publicação atômica, versões, locators, falhas e retry explícito.
- Grafo LangGraph com orquestrador, pesquisador condicionado à autorização da aplicação e tutor com RAG.
- Chat/citações efêmeros; busca por pedido explícito ou oferta aceita, sem busca na espera/recusa.
- Fontes temporárias na RAM, consulta e promoção de snapshots selecionados por endpoint protegido.
- SelectionGrant, idempotência, concorrência, falha de embedding, close antes/depois do commit e descarte.
- Interface de chat, biblioteca, fontes e progresso operacional; sem recursos pedagógicos adicionais.
- Coletor com DNS público obrigatório, IP pinado, Host/SNI/TLS preservados, redirects validados e corpo limitado.

Última suíte completa após os ajustes finais: **94 testes aprovados**, em contêiner, com banco
real e provedores controlados. A jornada integrada US1→US5 passou incluindo reinício e persistência
apenas da biblioteca autorizada. Regressões subsequentes são registradas no relatório local.

Na inspeção de navegador foram verificados estado vazio, pergunta sem evidência, oferta/recusa,
pedido explícito sem confirmação redundante, fontes disponíveis ao navegar e progresso da pesquisa.
O upload visual foi rejeitado pela revisão automática de permissões da ferramenta e não foi
contornado. Seu fluxo HTTP passou em schemas de teste isolados. Não houve persistência de fontes
do ensaio visual na biblioteca pessoal.

## Ainda pendente

- Configurar projeto/endpoint e credenciais para as integrações reais. G0 foi retirado pelo usuário em 2026-10-29; não se exige retenção zero externa.
- E2 Gemini real, E3 embeddings reais, E4 descoberta/coleta real, E6 respostas reais e revisão semântica.
- Completar as matrizes de avaliação comportamental/retensão, inspeção de todos os artefatos duráveis
  e acessibilidade/estados da UI; os testes atuais não equivalem à verificação integral de cada checklist.
- Completar comparação de schemas/enums/cliente HTTP, além das rotas e operationIds já comparados.
- Ensaiar recuperação de falhas na interface, upload visual autorizado e apresentação final.
- Calibrar limites, chunking, top-k e modelos a partir de experimentos permitidos; nenhuma meta nova foi aprovada.

## Limitações conhecidas do incremento

Fixture usa tutor extrativo e embedding por hash, sem interpretação semântica. HTML de pesquisa
é sintético e identificado como tal. URLs de fixture são identificadores, não páginas coletadas.
Reconhecimento textual de pesquisa é conservador para não promover citações ou negações a pedidos;
o comando explícito na tela Fontes continua disponível para formular pesquisas sem ambiguidade.
O coletor rejeita HTML comprimido e não faz fallback/retry automático. Essas escolhas devem ser
avaliadas em E4, não apresentadas como decisões permanentes. O baseline de retrieval cobre corpus
próprio e vetores de fixture; não é benchmark do modelo real.

**Não declarar o MVP integral ou a demonstração com dados reais prontos.** A implementação pode
ser revisada/exercitada localmente sem chave, mantendo todos os bloqueios externos.

## Atualizações finais do incremento

Foi acrescentado o runner de 12 cenários comportamentais (17 verificações aprovadas), comparados campos/literais dos schemas além de rotas e operationIds e verificados pesquisa vazia/parcial, quota e G0 bloqueado. Detalhes em [local-evaluations](local-evaluations.md). A consulta do cliente TypeScript segue checada pelo build; a equivalência integral de tipos/constraints continua pendente.

O [ensaio visual](US5-ui-checks.md) também confirmou retorno ao chat, referência temporária preservada na navegação e descarte ao encerrar. A biblioteca pessoal permaneceu vazia após o ensaio.

## Esclarecimento aprovado — 2026-10-29

**G0 externo não é mais uma pendência.** O usuário esclareceu que a exigência de não persistir vale para o armazenamento local. O comprovante e o bloqueio de retenção externa foram removidos do backend; as APIs exigem configuração/credenciais, não retenção zero. A interface informa envio externo e retenção gerida pelos provedores. Constituição corrigida para 1.0.1. Garantias locais e seleção explícita preservadas.

Validação desta revisão: build TypeScript/Vite em contêiner e **95 testes aprovados em 5.72s** na imagem final. Clientes reais foram testados com factories/doubles; nenhuma chamada externa real ocorreu. A configuração e avaliação das integrações reais continuam pendentes.

## Corpus representativo e integração Gemini — atualização

O corpus principal agora contém 12 artigos completos da web, 512.403 caracteres, 65.519 palavras e 32 perguntas ancoradas em passagens. O baseline real com Gemini embeddings e pgvector foi concluído sobre 345 trechos: Recall@5 de documentos 98,21% e cobertura das passagens rotuladas 92,86%. São métricas iniciais com rótulos não exaustivos, não qualidade de respostas do tutor. A revisão dos erros e limitações está em [E3-web-corpus.md](E3-web-corpus.md).

Credenciais Gemini estão configuradas sem exposição nas saídas. Uma jornada HTTP real com gemini-2.5-flash-lite passou em schema isolado. A avaliação de geração encontrou 503/timeouts e uma falha de classificação parcial; esses pontos continuam pendentes. Busca Brave ainda sem credencial. Nenhum resultado novo altera silenciosamente o modo de execução escolhido no .env do usuário.
