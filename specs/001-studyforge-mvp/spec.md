# Feature Specification: StudyForge — assistente pessoal de estudos (MVP)

**Feature Branch**: `001-studyforge-mvp`

**Created**: 2026-10-28

**Status**: Draft — cinco clarificações integradas; pronto para planejamento preliminar,
com metas, limites e refinamentos explicitamente pendentes de aprovação.

**Input**: Assistente pessoal de estudos multiagêntico com biblioteca Markdown, tutoria
fundamentada, pesquisa HTML temporária e ingestão de fontes web por seleção explícita.

**Constitution**: Esta especificação segue a constituição v1.0.0 em
[constitution.md](../../.specify/memory/constitution.md). O nome StudyForge é provisório.
Tecnologias já escolhidas serão detalhadas no planejamento.

## Clarifications

### Session 2026-10-28

- Q: Quando a pesquisa web pode começar? → A: Se os dados disponíveis na base de conhecimento
  não sustentarem a resposta ou a deixarem consideravelmente incompleta, a interface deve perguntar
  se o usuário aceita pesquisar. A recusa retorna à interface normal sem executar a pesquisa;
  a aceitação inicia o fluxo. Um pedido explícito de pesquisa inicia o fluxo sem nova confirmação.
- Q: Até quando as fontes web temporárias devem permanecer disponíveis? → A: Até encerrar
  explicitamente a conversa ou reiniciar a aplicação, o que ocorrer primeiro. Navegar entre
  telas não encerra a conversa. A regra se aplica às fontes não selecionadas; fontes já
  guardadas permanecem na biblioteca.
- Q: O histórico do chat deve sobreviver ao reinício da aplicação? → A: Não. Todas as conversas
  ficam apenas em memória e são descartadas no reinício, inclusive as que usam exclusivamente
  a biblioteca. A biblioteca permanece persistida.
- Q: Ao encerrar explicitamente uma conversa, o que acontece com suas mensagens? → A: Para a
  versão inicial, descartar toda a conversa e abrir um chat vazio, preservando a biblioteca.
  Aprimoramentos da experiência de conversa ficam para versões futuras, sem escopo definido.
- Q: O que a área progresso deve mostrar na versão inicial? → A: Acompanhamento operacional
  dos materiais em processamento, disponíveis ou com falha e dos estados de pesquisa e ingestão,
  sem notas, estimativa de domínio ou avaliação pedagógica.

## User Scenarios & Testing *(mandatory)*

As prioridades ordenam a entrega incremental; todas as jornadas abaixo pertencem ao MVP.
Cada jornada tem uma verificação isolada usando materiais e estados de teste conhecidos.
As jornadas de tutoria e seleção dependem dos materiais produzidos por upload ou pesquisa;
essa dependência não exige executar novamente todas as jornadas para testar cada uma.

### User Story 1 - Enviar materiais e acompanhar a biblioteca (Priority: P1)

Como pessoa que estuda, quero enviar arquivos Markdown e encontrá-los na biblioteca com um
estado claro, para saber o que já posso usar com o tutor e o que precisa de atenção.

**Why this priority**: Estabelece a entrada controlada dos materiais pessoais e a base do estudo.

**Independent Test**: Enviar um Markdown com conteúdo conhecido e um arquivo inválido;
verificar a biblioteca e a disponibilidade de cada material sem depender da pesquisa web.

**Acceptance Scenarios**:

1. **US1-1 — Dado** uma biblioteca vazia, **quando** eu a abrir, **então** vejo que ainda não há
   materiais e uma ação para enviar Markdown.
2. **US1-2 — Dado** um Markdown válido, **quando** eu o enviar, **então** o material aparece
   identificado como recebido/em processamento e ainda não pode fundamentar respostas.
3. **US1-3 — Dado** o processamento concluído com sucesso, **quando** eu consultar a biblioteca,
   **então** o material está disponível e posso identificar o arquivo de origem e consultá-lo.
4. **US1-4 — Dado** um arquivo de outro formato, vazio ou ilegível como texto Markdown,
   **quando** eu tentar enviá-lo, **então** o sistema informa o motivo da rejeição e não o
   disponibiliza como conhecimento.
5. **US1-5 — Dado** um material aceito cujo processamento falha ou é interrompido,
   **quando** eu consultar seu estado, **então** vejo a falha e uma orientação de recuperação;
   trechos parcialmente processados não são usados pelo tutor como material disponível.
6. **US1-6 — Dado** materiais disponíveis e outro com falha, **quando** eu abrir a biblioteca
   novamente, **então** cada item mantém seu estado identificável e a falha não oculta os demais.

### User Story 2 - Aprender com o tutor e verificar as referências (Priority: P1)

Como pessoa que estuda, quero conversar sobre os materiais disponíveis, receber explicações
e verificar as fontes para compreender o conteúdo e reconhecer os limites das respostas.

**Why this priority**: Entrega o valor central de aprender com os próprios materiais.

**Independent Test**: Preparar uma biblioteca conhecida e perguntas com resposta sustentada,
resposta parcial, evidências conflitantes e nenhuma evidência; avaliar explicação e referências.

**Acceptance Scenarios**:

1. **US2-1 — Dado** material disponível que sustenta minha pergunta, **quando** eu perguntar,
   **então** recebo uma explicação pertinente com referências ao material e à passagem usada.
2. **US2-2 — Dado** uma referência apresentada, **quando** eu a consultar, **então** consigo
   identificar a origem e o trecho efetivamente usado para sustentar a afirmação associada.
3. **US2-3 — Dado** que nenhuma fonte disponível sustenta a resposta, **quando** eu perguntar,
   **então** o tutor comunica a insuficiência sem inventar conteúdo fundamentado ou referências.
4. **US2-4 — Dado** suporte apenas parcial ou fontes conflitantes, **quando** eu perguntar,
   **então** o tutor delimita o que consegue responder, identifica a lacuna ou divergência e
   distingue inferências das afirmações sustentadas.
5. **US2-5 — Dado** apenas itens em processamento ou com falha, **quando** eu solicitar uma
   explicação, **então** esses itens não são citados como conhecimento disponível.
6. **US2-6 — Dado** um material que ordene ignorar regras, executar ferramentas ou guardar
   fontes, **quando** ele for consultado, **então** essas instruções não alteram permissões,
   papéis ou persistência.
7. **US2-7 — Dado** uma resposta em geração que falhe ou atinja um limite,
   **quando** o fluxo parar, **então** o resultado é identificado como parcial/interrompido,
   sem sinal de conclusão bem-sucedida nem exposição de segredos.

### User Story 3 - Pesquisar e estudar com fontes web temporárias (Priority: P2)

Como pessoa que estuda um assunto ainda não coberto pela biblioteca, quero pesquisar páginas
HTML e usá-las temporariamente com o tutor, sabendo quais fontes sustentam a explicação.

**Why this priority**: Amplia os assuntos disponíveis sem transferir ao sistema o controle
da biblioteca.

**Independent Test**: Usar uma pesquisa controlada com páginas HTML úteis, indisponíveis,
sem conteúdo extraível e de formato não suportado; verificar resultados e tutoria temporária.

**Acceptance Scenarios**:

1. **US3-1 — Dado** um assunto a pesquisar, **quando** eu solicitar a pesquisa,
   **então** o sistema reconhece meu pedido explícito e inicia o fluxo sem perguntar novamente
   se pode pesquisar; o orquestrador supervisiona o pesquisador e vejo a busca em andamento.
2. **US3-2 — Dado** páginas HTML encontradas e conteúdo extraído com sucesso,
   **quando** os resultados chegarem, **então** posso ver título ou identificação equivalente,
   endereço, prévia e condição temporária antes de escolher o que guardar.
3. **US3-3 — Dado** fontes temporárias utilizáveis e não selecionadas,
   **quando** eu estudar com o tutor, **então** ele pode usá-las e referenciá-las enquanto
   disponíveis, sem adicioná-las à biblioteca.
4. **US3-4 — Dado** uma resposta que use biblioteca e pesquisa temporária,
   **quando** eu consultar as referências, **então** a categoria e a origem de cada uma estão
   explícitas; a resposta não apresenta uma fonte temporária como parte da biblioteca.
5. **US3-5 — Dado** uma pesquisa sem fontes utilizáveis, **quando** ela terminar,
   **então** vejo que nenhuma fonte utilizável foi encontrada e o tutor não simula evidências.
6. **US3-6 — Dado** algumas fontes úteis e outras indisponíveis, de outro formato ou sem texto
   extraível, **quando** a pesquisa terminar, **então** vejo o resultado parcial e suas falhas;
   apenas o conteúdo efetivamente obtido pode sustentar a explicação.
7. **US3-7 — Dado** uma fonte temporária expirada, **quando** eu tentar usá-la, consultá-la
   ou selecioná-la, **então** vejo a expiração e a necessidade de nova obtenção da fonte;
   ela não é recuperada silenciosamente de conteúdo retido nem usada como evidência atual.
8. **US3-8 — Dado** uma página que tente instruir os agentes a persistir conteúdo,
   **quando** ela for extraída ou consultada, **então** o conteúdo continua sendo dado sem
   autoridade e nenhuma ingestão ocorre sem minha seleção.
9. **US3-9 — Dado** uma pergunta sem pedido explícito de pesquisa, **quando** o sistema identificar
   que os dados disponíveis na base de conhecimento não sustentam a resposta ou a deixam
   consideravelmente incompleta, **então** a interface pergunta se aceito pesquisar na web,
   sem iniciar o fluxo antes da minha resposta.
10. **US3-10 — Dado** a oferta de pesquisa por insuficiência da base de conhecimento,
    **quando** eu recusar, **então** a oferta é encerrada, a interface retorna ao estado normal
    e nenhuma busca, extração ou outra etapa do fluxo de pesquisa é executada.
11. **US3-11 — Dado** a mesma oferta, **quando** eu aceitar,
    **então** o fluxo de pesquisa começa, sem nova confirmação, com seu estado visível.
12. **US3-12 — Dado** uma oferta de pesquisa ainda sem resposta,
    **quando** o sistema aguardar minha decisão, **então** nenhuma etapa do fluxo de pesquisa
    é executada; detectar a lacuna ou apresentar a oferta não autoriza pesquisar antecipadamente.
13. **US3-13 — Dado** fontes temporárias não selecionadas em uma conversa ativa,
    **quando** eu navegar entre chat, biblioteca, progresso e seleção de fontes,
    **então** elas continuam disponíveis na mesma conversa.
14. **US3-14 — Dado** fontes temporárias não selecionadas,
    **quando** eu encerrar explicitamente a conversa ou reiniciar a aplicação,
    **então** o primeiro desses eventos encerra sua disponibilidade e descarta seu conteúdo;
    fontes já guardadas permanecem disponíveis na biblioteca.

### User Story 4 - Selecionar fontes para guardar (Priority: P2)

Como pessoa que estuda, quero inspecionar as fontes pesquisadas e escolher quais guardar,
para construir uma biblioteca sob meu controle e preservar a origem do conhecimento.

**Why this priority**: Conecta pesquisa e biblioteca sem persistência automática.

**Independent Test**: Preparar duas fontes temporárias; selecionar uma, repetir a seleção
e simular falha de ingestão. Inspecionar a biblioteca e os registros de persistência.

**Acceptance Scenarios**:

1. **US4-1 — Dado** fontes temporárias A e B utilizáveis, **quando** eu selecionar apenas A
   para guardar, **então** somente A é autorizada para ingestão, com processamento visível,
   e B permanece temporária.
2. **US4-2 — Dado** ingestão de A concluída, **quando** eu a consultar na biblioteca,
   **então** ela está disponível como fonte guardada e preserva endereço de origem,
   identificação, instante de obtenção e vínculo com o conteúdo que autorizei.
3. **US4-3 — Dado** A já selecionada, em processamento ou guardada,
   **quando** eu repetir a mesma seleção para o mesmo conteúdo obtido,
   **então** o sistema informa seu estado sem criar itens ou processamentos duplicados.
4. **US4-4 — Dado** falha durante a ingestão de A, **quando** eu verificar o resultado,
   **então** vejo que ela não está disponível, com orientação de recuperação;
   B não é ingerida e partes incompletas de A não são apresentadas como conhecimento válido.
5. **US4-5 — Dado** que não selecionei uma fonte, **quando** eu conversar, citar, navegar,
   encerrar o fluxo ou ocorrer falha, **então** seu conteúdo e derivados não aparecem em
   armazenamento durável, inclusive histórico, resumos e registros de diagnóstico.
6. **US4-6 — Dado** uma seleção sobre material expirado ou diferente do inspecionado,
   **quando** não for possível confirmar que a autorização corresponde ao conteúdo obtido,
   **então** o sistema não guarda o material silenciosamente e informa a necessidade de
   obter/revisar a fonte antes de uma seleção válida.

### User Story 5 - Navegar e compreender o estado do estudo (Priority: P2)

Como pessoa que estuda, quero navegar entre chat, biblioteca, progresso e seleção de fontes,
com estados compreensíveis para decidir a próxima ação. Progresso é o acompanhamento operacional
dos materiais, pesquisas e ingestões, sem avaliação de aprendizagem.

**Why this priority**: Torna os fluxos e suas limitações visíveis e utilizáveis.

**Independent Test**: Abrir cada destino com estados preparados de vazio, carregamento,
sucesso, falha parcial, erro e expiração, sem depender de uma avaliação pedagógica.

**Acceptance Scenarios**:

1. **US5-1 — Dado** a interface do MVP, **quando** eu usar a navegação,
   **então** consigo chegar a chat, biblioteca, progresso e seleção de fontes.
2. **US5-2 — Dado** uma operação em andamento ou uma coleção vazia,
   **quando** eu abrir o destino correspondente, **então** carregamento e ausência de itens
   são distinguíveis e a próxima ação disponível é compreensível.
3. **US5-3 — Dado** falha parcial, erro ou expiração,
   **quando** eu consultar o fluxo, **então** vejo o que permanece utilizável, o que falhou e
   como prosseguir, sem confundir resultado incompleto com sucesso.
4. **US5-4 — Dado** materiais em processamento, disponíveis ou com falha e operações de pesquisa
   e ingestão com estados conhecidos, **quando** eu abrir progresso, **então** consigo identificar
   o estado operacional dos materiais e operações pertinentes, inclusive conclusão, falha parcial
   ou interrupção quando aplicável, sem notas, estimativa de domínio ou avaliação pedagógica.
5. **US5-5 — Dado** conversas sobre a biblioteca, fontes temporárias ou ambas,
   **quando** eu reiniciar a aplicação, **então** nenhuma conversa ou histórico é restaurado;
   os materiais já disponíveis na biblioteca permanecem disponíveis.
6. **US5-6 — Dado** uma conversa com perguntas, respostas, referências e possíveis fontes
   temporárias não selecionadas, **quando** eu encerrar explicitamente a conversa,
   **então** toda a conversa e essas fontes são descartadas, um chat vazio é aberto e os
   materiais já disponíveis na biblioteca permanecem disponíveis.

### Edge Cases

- Arquivo com extensão Markdown mas sem texto legível; conteúdo vazio; formato não suportado.
  A validação não pode depender somente do nome do arquivo.
- Nome repetido de arquivo não comprova identidade de conteúdo. A política de duplicação de
  uploads permanece proposta de refinamento; a proteção US4-3 já vale para seleções web repetidas.
- Página acessível no navegador mas sem conteúdo HTML extraível; endereço indisponível;
  resultado que aponte para PDF ou outro formato fora do MVP.
- Uma fonte falha enquanto outras funcionam; resultados incompletos não podem parecer completos.
- Encerramento explícito da conversa ou reinício da aplicação concorre com a seleção de uma
  fonte temporária. Sem confirmação de validade e correspondência da autorização, a gravação
  não prossegue; ingestão já autorizada deve ter
  resultado explícito, sem substituir o material por uma nova obtenção silenciosa.
- Referência externa deixa de responder após extração: distinguir o texto efetivamente
  consultado ainda disponível do acesso ao endereço externo, sem afirmar que houve nova leitura.
- Fontes contraditórias, trechos irrelevantes e pergunta fora da cobertura disponível.
- Uma lacuna na base de conhecimento gera uma oferta de pesquisa, não uma busca automática.
  Recusa ou ausência de aceitação não pode disparar busca ou extração em segundo plano.
- Instruções hostis em arquivos, páginas, trechos recuperados e resultados do pesquisador.
- Interrupção, limite de execução ou repetição após falha não pode publicar ingestão incompleta,
  duplicar uma seleção já aceita ou ampliar a autorização.
- Respostas, resumos e registros de erro podem reproduzir conteúdo temporário; o mesmo veto à
  persistência de fontes não selecionadas se aplica a essas derivações.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE aceitar uploads locais somente de texto Markdown válido para leitura,
  rejeitando outros formatos, conteúdo vazio e arquivos ilegíveis com motivo compreensível.
- **FR-002**: A biblioteca DEVE identificar os materiais enviados e distinguir recebido/em
  processamento, disponível e falhou; somente materiais disponíveis podem fundamentar a tutoria.
- **FR-003**: O usuário DEVE conseguir consultar a origem e o conteúdo de um material disponível;
  uma falha em outro material não pode ocultar os itens utilizáveis.
- **FR-004**: O chat DEVE permitir perguntas e explicações pertinentes baseadas nos materiais
  recuperados que estejam disponíveis ao tutor.
- **FR-005**: Afirmações atribuídas a fontes DEVEM ter referências consultáveis que identifiquem
  o material e a passagem usada; a referência não pode apontar suporte inexistente.
- **FR-006**: O tutor DEVE reconhecer evidência ausente, parcial ou conflitante e distinguir
  inferência de informação sustentada, sem inventar fatos ou referências para preencher lacunas.
- **FR-007**: O orquestrador DEVE supervisionar o fluxo; o pesquisador DEVE buscar e extrair fontes
  web HTML; o tutor DEVE usar recuperação das fontes disponíveis para ensinar. Esses agentes
  não podem autorizar persistência ou ultrapassar as permissões de seus papéis.
- **FR-008**: O sistema DEVE permitir solicitar pesquisa por assunto e mostrar busca em andamento,
  fontes utilizáveis, nenhuma fonte utilizável, falha parcial ou erro. Um pedido explícito de
  pesquisa DEVE iniciar o fluxo sem confirmação adicional. Na ausência desse pedido, se a base
  de conhecimento disponível não sustentar a resposta ou a deixar consideravelmente incompleta,
  a interface DEVE oferecer a pesquisa e aguardar a escolha. Aceitar DEVE iniciar o fluxo;
  recusar DEVE encerrar a oferta e retornar à interface normal sem executar qualquer etapa de
  pesquisa. Enquanto não houver aceitação, o sistema NÃO DEVE executar busca, extração ou outras
  etapas do fluxo de pesquisa. A detecção de insuficiência não autoriza o início automático.
- **FR-009**: Cada resultado web DEVE apresentar identificação, endereço, prévia do conteúdo
  efetivamente extraído e estado de disponibilidade; formato não suportado não pode parecer fonte
  extraída com sucesso.
- **FR-010**: O tutor DEVE poder usar fontes pesquisadas temporariamente sem exigir sua ingestão.
  Respostas e referências DEVEM distinguir biblioteca e fontes temporárias, inclusive em uso misto.
- **FR-011**: O usuário DEVE poder inspecionar as fontes e selecionar explicitamente quais guardar.
  Buscar, ler, citar ou conversar não constitui seleção nem autorização de ingestão.
- **FR-012**: Somente conteúdo de fontes web explicitamente selecionadas DEVE poder ser ingerido
  e persistido, com autorização verificável vinculada ao material obtido.
- **FR-013**: A fonte guardada DEVE preservar identificação, endereço de origem, instante de
  obtenção e vínculo entre seleção, conteúdo autorizado e referências usadas.
- **FR-014**: Selecionar repetidamente a mesma fonte e o mesmo conteúdo obtido NÃO DEVE produzir
  duplicação de itens ou processamentos, inclusive após interrupção e nova tentativa.
- **FR-015**: Ingestão DEVE ter estados observáveis de processamento, disponibilidade e falha;
  partes incompletas não podem ser oferecidas ao tutor como conhecimento validado.
- **FR-016**: Conteúdo web não selecionado e suas reproduções ou derivações NÃO DEVEM ser
  persistidos na biblioteca, índices, caches duráveis, histórico, respostas salvas, resumos,
  registros de diagnóstico ou outros armazenamentos. Metadados permitidos não podem conservar
  nem permitir reconstruir esse conteúdo.
- **FR-017**: Fontes web não selecionadas DEVEM ficar disponíveis temporariamente a partir da
  obtenção de conteúdo utilizável até o encerramento explícito da conversa ou o reinício da
  aplicação, o que ocorrer primeiro. Navegar entre telas NÃO DEVE encerrar a conversa nem expirar
  essas fontes. No primeiro desses eventos, seu conteúdo DEVE ser descartado; fontes expiradas
  não podem ser usadas ou selecionadas como se ainda estivessem disponíveis. A indisponibilidade
  DEVE ser comunicada conforme US3-7, sem conservar conteúdo descartado. Fontes já guardadas
  permanecem na biblioteca. O reinício também descarta o histórico conforme FR-018.
- **FR-018**: Todo o histórico de chat DEVE permanecer apenas em memória e ser descartado ao
  reiniciar a aplicação, sem retomada de conversas após o reinício. A regra DEVE abranger
  perguntas, respostas e referências de todas as conversas, inclusive as baseadas exclusivamente
  na biblioteca. O sistema NÃO DEVE salvar cópias duráveis do histórico para recuperação.
  A biblioteca DEVE permanecer persistida, respeitando o estado de cada material. FR-016 continua
  aplicável em sucesso, falha e interrupção. Ao encerrar explicitamente uma conversa, o sistema
  DEVE descartar toda a conversa, incluindo perguntas, respostas, referências e contexto associado,
  além de suas fontes temporárias não selecionadas, e abrir um chat vazio, preservando a biblioteca.
- **FR-019**: A interface DEVE oferecer navegação para chat, biblioteca, progresso e seleção de
  fontes. Progresso DEVE mostrar o acompanhamento operacional dos materiais em processamento,
  disponíveis ou com falha e dos estados de pesquisa e ingestão. Esses estados DEVEM refletir
  o resultado efetivo das operações, distinguindo conclusão, falha parcial e interrupção quando
  aplicável. Progresso NÃO DEVE apresentar notas, estimativa de domínio ou avaliação pedagógica.
- **FR-020**: Os destinos pertinentes DEVEM distinguir carregamento, ausência de materiais,
  nenhuma fonte utilizável, falha parcial, erro e expiração, com orientações para prosseguir.
- **FR-021**: Arquivos, páginas e trechos recebidos DEVEM permanecer dados não confiáveis:
  instruções neles não podem alterar regras, papéis, permissões ou autorização de gravação.
- **FR-022**: Validação, normalização, divisão em trechos e gravação DEVEM obedecer a regras
  determinísticas e verificáveis; decisões livres dos agentes não substituem essas regras.
- **FR-023**: O sistema DEVE limitar duração, chamadas, ciclos, volume de dados e repetições
  conforme cada fluxo; ao atingir limites, DEVE informar interrupção e preservar consistência.
  Valores serão propostos e acordados antes da implementação do fluxo afetado.
- **FR-024**: Erros DEVEM identificar de modo compreensível a etapa afetada e a orientação de
  recuperação sem revelar segredos ou conteúdo cuja retenção seja vedada. Estados parciais
  não podem ser apresentados como conclusão bem-sucedida.
- **FR-025**: A entrega DEVE incluir testes relevantes do fluxo completo e das falhas descritas,
  avaliação repetível da recuperação e avaliação do comportamento dos agentes, com resultados
  registrados sem conservar conteúdo temporário não autorizado de usuários.

### Key Entities *(include if feature involves data)*

- **Material da biblioteca**: conteúdo autorizado para uso persistente, identificação,
  categoria de origem (upload ou web selecionada), referência de origem e estado de processamento.
- **Fonte web temporária**: endereço, identificação, texto efetivamente obtido, instante de
  obtenção, contexto da pesquisa, vínculo à conversa e estado temporário/indisponível/expirado;
  não é item da biblioteca. Seu conteúdo não selecionado é descartado ao encerrar explicitamente
  a conversa ou reiniciar a aplicação, o que ocorrer primeiro.
- **Seleção de fonte**: manifestação explícita do usuário, fonte e conteúdo a que se aplica,
  instante da escolha e resultado da ingestão; repetir a mesma escolha não cria nova autorização
  para conteúdo diferente.
- **Referência de resposta**: vínculo entre afirmação, fonte, passagem consultada e categoria
  biblioteca/temporária; sua disponibilidade respeita o ciclo de vida da fonte.
- **Conversa**: perguntas, respostas e referências mantidas apenas em memória. Nenhuma conversa
  é restaurada após reiniciar a aplicação, mesmo quando usa exclusivamente a biblioteca.
  Encerrar explicitamente a conversa descarta todas as suas mensagens e o contexto associado,
  assim como suas fontes temporárias não selecionadas, e abre um chat vazio. A biblioteca permanece.
- **Operação acompanhável**: atividade de upload, processamento, pesquisa ou ingestão com estado,
  resultado parcial ou completo e falha compreensível. A área progresso apresenta esse
  acompanhamento operacional e os estados dos materiais; não representa progresso pedagógico.

### Evidence, Trust and Data Lifecycle *(mandatory; justify non-applicable items)*

**Início da pesquisa**: Um pedido explícito de pesquisa já autoriza iniciar o fluxo. Sem esse
pedido, a insuficiência da base de conhecimento apenas aciona a oferta na interface; o fluxo
depende da aceitação do usuário. Recusar encerra a oferta e retorna à interface normal sem
executar pesquisa. Essa autorização de busca não autoriza persistência de fontes.

**Origem e autoridade**: O envio local expressa a intenção de adicionar o Markdown à biblioteca,
sujeito à validação. A obtenção web expressa apenas uso temporário. A seleção explícita autoriza
a ingestão do conteúdo correspondente; agentes não podem produzir essa autorização.

**Ciclo de vida**: Upload validado → processamento → disponível ou falhou.
Fonte web obtida → temporária utilizável → seleção autorizada e ingestão, ou expiração e descarte.
Uma fonte não extraída com sucesso fica indisponível para fundamentação. A seleção, por si só,
não comprova conclusão da ingestão. Fontes não selecionadas permanecem disponíveis desde a
obtenção de conteúdo utilizável até encerrar explicitamente a conversa ou reiniciar a aplicação,
o que ocorrer primeiro; nesse evento, seu conteúdo é descartado. Navegar entre telas não encerra
a conversa. Fontes já guardadas permanecem na biblioteca. O histórico de todas as conversas
fica apenas em memória e é descartado no reinício da aplicação. Encerrar explicitamente uma
conversa também descarta todo o seu conteúdo e contexto associado e abre um chat vazio,
preservando a biblioteca.

**Referências consultáveis**: Materiais guardados permitem consultar o conteúdo autorizado e sua
origem; fontes temporárias permitem consulta enquanto disponíveis. Após expiração, a interface
deve comunicar indisponibilidade sem reproduzir o conteúdo descartado. Não há histórico durável
nem retomada de conversas após reiniciar a aplicação. Ao encerrar explicitamente a conversa,
suas mensagens e referências são descartadas e não permanecem acessíveis no chat vazio aberto
em seguida.

**Retenção**: FR-016 abrange todos os caminhos de gravação, inclusive conteúdo derivado de
respostas. Metadados operacionais só podem ser retidos se não reproduzirem nem reconstruírem
conteúdo vedado; os campos permitidos e a comprovação do descarte serão detalhados no plano.
Falhas, novas tentativas e encerramento não autorizam ampliar retenção.

**Verificação transversal**: Testar US2-6 e US3-8 com instruções hostis; US4-1 e US4-5 com
inspeção de todos os destinos de armazenamento; US3-7 após expiração; US1-5, US2-7 e US4-4
com interrupções. Testes usam materiais próprios/autorizados para avaliação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

Os resultados abaixo são verificações de comportamento exigido. Limiares estatísticos de
qualidade, capacidade e desempenho ainda são propostas; não são decisões atribuídas ao usuário.

- **SC-001**: Nos cenários US1, o usuário consegue distinguir material disponível, em processamento,
  rejeitado e com falha; somente o primeiro fundamenta respostas. Evidência: execução da jornada.
- **SC-002**: Nos cenários US2 e US3, o usuário consegue verificar origem, passagem e categoria das
  referências; ausência, insuficiência e conflito de evidências são comunicados conforme o caso.
- **SC-003**: Em US4, a biblioteca recebe apenas a fonte selecionada; repetição da mesma seleção
  mantém um único item/processamento para o mesmo material, e a fonte não selecionada não deixa
  conteúdo ou derivados duráveis nos destinos inspecionados.
- **SC-004**: Nas falhas, interrupções e expirações descritas, o usuário identifica o estado e
  uma orientação para prosseguir; nenhum item incompleto é apresentado como disponível.
  US3-13/14 verificam que navegar preserva a disponibilidade temporária, enquanto encerramento
  explícito da conversa ou reinício da aplicação descarta o conteúdo não selecionado sem remover
  fontes já guardadas da biblioteca.
- **SC-005**: Os cenários hostis preservam papéis, permissões e controle da persistência. O relatório
  identifica, por caso, resultado esperado, observado e eventual violação.
- **SC-006**: A avaliação de recuperação registra, para perguntas e materiais de referência,
  presença de fonte relevante entre os resultados e uso de origem correta na resposta.
  A avaliação dos agentes registra fidelidade, reconhecimento de lacunas e respeito aos papéis.
- **SC-007**: A demonstração das jornadas registra se a pessoa concluiu enviar → estudar →
  pesquisar → selecionar → consultar fonte guardada e se distinguiu biblioteca de temporárias,
  com observações de dúvidas e impedimentos. Isso não mede domínio do conteúdo.
- **SC-008**: Em US5-1/4, o usuário acessa progresso e identifica corretamente os estados
  operacionais dos materiais, pesquisas e ingestões apresentados, comparando-os com os estados
  conhecidos do cenário de teste. Nenhuma nota, estimativa de domínio ou avaliação pedagógica
  é exibida como progresso.
- **SC-009**: Em US3-1 e US3-9 a US3-12, a pesquisa começa apenas após pedido explícito ou
  aceitação da oferta: a recusa retorna à interface normal sem execução do fluxo, a espera
  não dispara pesquisa antecipada e pedidos explícitos não geram confirmação redundante.
- **SC-010**: Em US5-5/6, após reiniciar a aplicação ou encerrar explicitamente a conversa,
  nenhuma pergunta, resposta, referência ou contexto da conversa descartada permanece no chat.
  O encerramento explícito abre um chat vazio. Nenhuma pergunta, resposta ou referência de
  conversas anteriores é restaurada; os materiais disponíveis da biblioteca permanecem utilizáveis.
  A inspeção dos destinos duráveis não encontra histórico salvo para recuperação de conversas.

### Propostas numéricas para discussão — não aprovadas

| Dimensão | Proposta inicial | Como verificar e decidir |
|----------|------------------|-------------------------|
| Recuperação | 20 perguntas rotuladas; fonte pertinente entre os 5 primeiros resultados em pelo menos 80% dos casos | Revisar perguntas, relevância esperada e meta antes de adotá-las. |
| Agentes | 20 casos cobrindo evidência, lacunas, conflito, papéis e conteúdo hostil; avaliar respostas sustentadas em pelo menos 90% dos casos respondíveis | Calibrar julgamento humano e limiar; violações de permissão e persistência são falhas contratuais, não compensadas pela média. |
| Volume inicial | Biblioteca de referência com 50 arquivos de até 1 MiB; até 5 fontes HTML utilizáveis por pesquisa | Validar representatividade com os materiais reais e recursos disponíveis. |
| Desempenho percebido | Em 95% dos ensaios, estado inicial visível em até 2 s e resposta final do tutor em até 30 s | Definir condições de medição; registrar pesquisa e ingestão separadamente, sem prometer prazo de serviços externos. |
| Usabilidade | Uma sessão guiada do fluxo completo com o responsável pelo projeto | Registrar conclusão das tarefas e clareza das fontes/estados; discutir necessidade de mais sessões. |

Esses números não são critérios de aprovação vigentes nem limites de produção. A revisão deve
registrar valores aceitos, condições e justificativa antes de usar as metas para aprovar a entrega.
O planejamento deve propor também limites de execução e prazo de processamento por operação.

### Cobertura de aceite e avaliação

| Requisitos | Evidência de aceite |
|------------|--------------------|
| FR-001 a FR-003 | US1-1 a US1-6, SC-001 |
| FR-004 a FR-006 | US2-1 a US2-5, SC-002 e avaliação de recuperação |
| FR-007 a FR-010 | US3-1 a US3-12, US2-6, avaliação de papéis e SC-005/006/009 |
| FR-011 a FR-015 | US4-1 a US4-4 e US4-6, SC-003/004 |
| FR-016 a FR-018 | US4-5, US3-7/13/14, US5-5/6 e SC-004/010 |
| FR-019 a FR-020 | US5-1 a US5-4 e SC-008 |
| FR-021 a FR-022 | US2-6, US3-8, US4-3/6 e verificação de processamento com entradas repetidas |
| FR-023 a FR-024 | US1-5, US2-7, US3-6, US4-4 e US5-3; limites após acordo dos valores |
| FR-025 | Testes das jornadas, avaliações repetíveis e relatório de resultados por caso |

## Assumptions

### Premissas e dependências

- Uso pessoal por uma pessoa; contas compartilhadas, colaboração e múltiplos usuários não são
  necessidades aprovadas. Durante o planejamento em 2026-10-28, o usuário confirmou acesso
  somente nesta máquina, via localhost. Exposição em LAN/internet não está aprovada.
- Páginas HTML acessíveis e extraíveis são o alvo da pesquisa; contornar login, restrições de
  acesso ou proteções de sites não integra o MVP.
- A aceitação de Markdown refere-se a texto legível e com conteúdo; não exige um padrão de
  formatação pedagógica específico. Codificação, limites e identificação serão refinados no plano.
- Recebido/em processamento pode ser apresentado em um único estado enquanto ainda não disponível;
  não se pressupõe percentual, estimativa de término ou acompanhamento em tempo real.
- A stack fornecida pelo usuário está registrada em plan.md, com versões candidatas verificadas
  e experimentos prévios à consolidação, sem transformar ferramentas em funcionalidades.
  O desenvolvimento segue o isolamento e
  as demais regras da constituição.
- Pesquisa depende da disponibilidade das fontes externas e da obtenção de conteúdo suficiente.
  A indisponibilidade deve ser observável e não pode produzir suporte inventado.
- Recuperação e agentes dependem de um conjunto de avaliação com perguntas, fontes e julgamentos
  esperados revisados. As propostas numéricas acima exigem discussão antes da aprovação.

### Fora do escopo

- Uploads locais diferentes de Markdown e pesquisa/ingestão de formatos web diferentes de HTML.
- Agente avaliador pedagógico, inferência de domínio, notas e avaliação de aprendizagem.
- Quizzes, repetição espaçada, gamificação, calendário e funcionalidades para múltiplos usuários.
- Integrações externas extensas e recursos administrativos não descritos nas jornadas.
- Histórico durável de conversas ou retomada de chat após reiniciar a aplicação.
- Aprimoramentos da experiência de conversa ficam para versões futuras, sem funcionalidade
  adicional definida ou aprovada para o MVP.
- Registro de atividades de estudo, notas e indicadores pedagógicos como conteúdo da área progresso.
- Compromissos com metas numéricas ainda não aprovadas; sua presença como proposta não as
  transforma em critérios de aprovação vigentes.

### Riscos

- **Retenção indireta**: Uma resposta ou um registro pode conservar conteúdo não selecionado;
  exige verificação transversal, não apenas inspeção da biblioteca.
- **Confusão de procedência**: Uma referência temporária pode parecer guardada ou utilizável após
  expiração; rótulos, consulta e descarte precisam seguir a mesma regra.
- **Autoridade indevida**: Conteúdo hostil pode tentar alterar permissões; verificar arquivos,
  pesquisa e tutoria, inclusive tentativas de gravação.
- **Ingestão inconsistente**: Falha, repetição e expiração concorrente podem duplicar ou publicar
  partes incompletas; autorização e resultado precisam permanecer verificáveis.
- **Qualidade aparente**: Resposta fluente pode usar fonte irrelevante ou suporte inventado;
  avaliar recuperação e comportamento separadamente.
- **Expansão de escopo**: Tratar progresso operacional como avaliação pedagógica ou promover
  aprimoramentos futuros de conversa a requisitos do MVP pode criar funcionalidades não aprovadas.
- **Dependências externas**: Indisponibilidade e mudança de páginas afetam a evidência obtida;
  preservar a origem do conteúdo efetivamente consultado sem buscar substituto silencioso.

### Decisões pendentes

- **D1 — Progresso (resolvida)**: Acompanhamento operacional dos materiais em processamento,
  disponíveis ou com falha e dos estados de pesquisa e ingestão, sem notas, estimativa de domínio
  ou avaliação pedagógica.
- **D2 — Disponibilidade temporária (resolvida)**: Fontes não selecionadas ficam disponíveis
  até encerrar explicitamente a conversa ou reiniciar a aplicação, o que ocorrer primeiro.
  Navegar entre telas não encerra a conversa; fontes já guardadas permanecem na biblioteca.
- **D3 — Histórico após reinício (resolvida)**: Todas as conversas ficam apenas em memória e
  são descartadas ao reiniciar a aplicação. Encerrar explicitamente uma conversa descarta todo
  o seu conteúdo, contexto e fontes temporárias não selecionadas e abre um chat vazio.
  A biblioteca permanece persistida. Aprimoramentos de conversa ficam para versões futuras.

Outros refinamentos a discutir antes dos fluxos afetados: aprovar ou substituir as propostas
numéricas; definir limites de arquivo, pesquisa e execução; estabelecer a identidade de versões
para seleção e a política de uploads repetidos. Esses pontos não foram respondidos nas cinco
perguntas da clarificação; o pedido de planejamento autorizou recomendações provisórias para
testes iniciais, a ajustar conforme os resultados, sem convertê-las em metas finais aprovadas.
O acesso localhost foi confirmado durante o planejamento. A garantia de retenção é local, conforme esclarecimento do usuário em 2026-10-29; não se exige gate externo G0 nem retenção zero nos provedores;
nenhuma exceção à constituição foi autorizada. Não há valores finais aprovados implícitos.

**Próxima etapa**: `/speckit-plan` para detalhar a stack escolhida e propor soluções aos
refinamentos acima. As cinco decisões desta sessão estão incorporadas. O plano deve manter
os pontos restantes explícitos e submetê-los à discussão antes de consolidar a implementação;
propostas numéricas não podem ser tratadas como aprovadas. Se exigirem outra decisão de produto,
realizar uma nova sessão de `/speckit-clarify` antes de finalizar as tarefas afetadas.


### Esclarecimento de retenção — 2026-10-29

O usuário confirmou: se os dados não ficarem persistidos localmente, a exigência está atendida. Fontes não selecionadas e conversas continuam somente em RAM local; biblioteca exige seleção explícita. Retenção em APIs externas segue suas políticas, com aviso de envio. Não é necessário comprovar retenção zero nem bloquear integração por esse motivo.
