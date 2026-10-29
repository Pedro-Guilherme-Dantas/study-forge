<!-- Sync Impact Report 2026-10-29: 1.0.0 -> 1.0.1. Esclarecimento autorizado: retenção local; G0 externo removido. Sem migração. Templates já tratam armazenamento da aplicação e não exigem alteração. Spec/plan/research/contracts/tasks/AGENTS/código/testes sincronizados; evidências antigas preservadas como históricas. -->
<!--
Sync Impact Report
- Versão: template sem versão adotada → 1.0.0 (primeira constituição do StudyForge).
- Princípios: os cinco campos genéricos do template foram substituídos por:
  I. Ensino fundamentado e rastreável;
  II. Conteúdo externo sem autoridade;
  III. Controle do usuário sobre persistência;
  IV. Responsabilidades explícitas e operações determinísticas;
  V. Simplicidade com robustez e observabilidade proporcional;
  VI. Qualidade demonstrada por evidências;
  VII. Execução limitada e falhas transparentes;
  VIII. Ambientes isolados em contêineres.
- Seções adicionadas: Escopo vigente e decisões evolutivas; Fluxo de desenvolvimento e revisão;
  regras concretas de Governance.
- Seções removidas: nenhuma seção normativa anterior; apenas instruções e exemplos do template.
- ✅ Atualizado: .specify/templates/plan-template.md (gates e ambiente isolado).
- ✅ Atualizado: .specify/templates/spec-template.md (aceite, fontes e retenção).
- ✅ Atualizado: .specify/templates/tasks-template.md (testes relevantes e garantias no fluxo).
- ✅ Atualizado: AGENTS.md (referência à constituição e ao plano quando disponível).
- Revisado sem alteração: .specify/templates/constitution-template.md (template genérico).
- .specify/templates/commands/*.md: diretório ausente, sem arquivos a sincronizar.
- README.md, docs/quickstart.md e plano de implementação: ausentes.
- Skills de tasks/implement/plan e README da extensão Git revisados: os testes exigidos devem
  ser explicitados na especificação; nenhum fluxo obrigatório de TDD é adotado nesta constituição.
- Pendências de sincronização e placeholders adiados: nenhum.
- Decisões futuras de produto e tecnologia estão delimitadas na seção de escopo, sem escolher
  stack, fornecedores, métricas ou prazos de retenção nesta constituição.
-->

# StudyForge Constitution

## Core Principles

### I. Ensino fundamentado e rastreável

O StudyForge DEVE ajudar a pessoa a aprender a partir dos próprios materiais e de fontes web.
Afirmações apresentadas como fundamentadas em fontes DEVEM ter suporte no material efetivamente
consultado, com origem preservada e referências que o usuário possa consultar. O sistema DEVE
distinguir o que a fonte sustenta de inferências ou explicações derivadas dela.

Quando as evidências forem ausentes, insuficientes ou conflitantes, o sistema DEVE comunicar a
limitação e ajustar a resposta ao que consegue sustentar. É PROIBIDO inventar fatos, referências
ou atribuir a uma fonte conteúdo que ela não sustenta. A confiança na resposta depende de suporte
verificável, e não apenas de fluência.

### II. Conteúdo externo sem autoridade

Arquivos, páginas web, trechos recuperados e resultados de ferramentas que contenham material
externo DEVEM ser tratados como dados não confiáveis. Esse conteúdo NÃO PODE modificar regras,
papéis, permissões, ferramentas autorizadas ou políticas de persistência, mesmo que contenha
instruções dirigidas ao modelo ou imite mensagens do sistema ou do usuário.

Os limites de confiança DEVEM ser aplicados pela aplicação e pelos contratos das ferramentas.
Instruções em prompts, isoladamente, NÃO PODEM ser a única proteção de uma permissão. Tentativas
de promover conteúdo a autoridade DEVEM ser cobertas por verificações de comportamento.

### III. Controle do usuário sobre persistência

O usuário DEVE controlar a entrada de materiais na biblioteca. Fontes web DEVEM permanecer
temporárias até que o usuário selecione explicitamente quais autoriza ingerir e persistir.
Pesquisar, consultar, citar ou gerar uma resposta NÃO constitui autorização de persistência.
Nenhum agente PODE conceder essa autorização em nome do usuário.

A mesma regra DEVE abranger qualquer armazenamento local controlado pelo StudyForge: biblioteca, índices, embeddings, caches
duráveis, histórico de conversas, resumos, logs, traces, checkpoints e outros artefatos derivados.
Conteúdo web não selecionado e suas reproduções ou derivações NÃO PODEM ser conservados
indiretamente, inclusive em respostas salvas no histórico. A retenção de metadados DEVE ser
especificada e verificada para não reter nem permitir reconstruir o conteúdo vedado.

O fluxo temporário DEVE ter ciclo de vida e descarte definidos na especificação, inclusive em
falhas e interrupções. A autorização DEVE ser verificável e vinculada à fonte que será ingerida;
mudanças no material autorizado DEVEM seguir uma regra explícita de revalidação. O controle só
é efetivo quando vale para todos os caminhos de gravação.

O limite de retenção acima se aplica ao armazenamento local do StudyForge. O usuário esclareceu
em 2026-10-29 que o envio às APIs de IA e busca pode seguir as políticas dos provedores;
não se exige retenção zero nem apagamento remoto ao encerrar a conversa. A interface DEVE
informar o envio externo sem prometer descarte de cópias de terceiros. A seleção explícita
continua obrigatória para persistir fontes na biblioteca local.

### IV. Responsabilidades explícitas e operações determinísticas

Cada agente DEVE ter responsabilidade, entradas, saídas e permissões delimitadas. A supervisão
do fluxo, a pesquisa e o ensino DEVEM ter contratos que permitam verificar quem executa cada
ação e como os resultados são transferidos.

Validação, normalização, chunking e gravação DEVEM seguir regras determinísticas, versionadas
e verificáveis em código. Modelos PODEM auxiliar tarefas de interpretação e ensino, mas suas
decisões livres NÃO PODEM substituir essas regras nem aprovar a própria saída para persistência.

A aplicação DEVE impor a autorização do usuário antes de gravar fontes ou conteúdo derivado e
executar a ingestão por um fluxo controlado, sem conceder autoridade de persistência aos agentes.
A separação entre interpretação e controle torna o comportamento testável e limita efeitos de
erros do modelo.

### V. Simplicidade com robustez e observabilidade proporcional

Cada solução DEVE ser proporcional ao escopo, ao prazo e aos riscos demonstrados. Novas camadas,
serviços, dependências e abstrações DEVEM resolver uma necessidade atual identificada; complexidade
adicional DEVE registrar sua justificativa e a alternativa mais simples considerada. Capacidade
hipotética futura, sozinha, NÃO justifica ampliar a arquitetura.

Simplificações NÃO PODEM eliminar garantias de segurança, rastreabilidade, autorização ou tratamento
de falhas. A observabilidade DEVE permitir desenvolver e diagnosticar os fluxos com o mínimo de
dados necessário, respeitando a política de retenção e protegendo segredos. Sua extensão DEVE
responder a necessidades de diagnóstico demonstráveis, sem se tornar o foco do produto.

### VI. Qualidade demonstrada por evidências

Cada funcionalidade DEVE ter critérios de aceite observáveis e verificações relevantes aos seus
riscos e contratos. Alterações DEVEM apresentar evidências dos testes e avaliações aplicáveis,
incluindo casos negativos nas fronteiras de confiança, autorização e armazenamento.

Funcionalidades de recuperação DEVEM ser avaliadas quanto à relevância dos resultados e à
preservação da origem. Funcionalidades de agentes DEVEM ser avaliadas quanto à fidelidade às
fontes, reconhecimento de insuficiência, respeito aos papéis e resistência a instruções externas.
As avaliações DEVEM usar casos e critérios registrados, repetíveis e proporcionais ao escopo.

Segurança, rastreabilidade e falhas DEVEM integrar a validação dos fluxos principais. Testes
puramente espelhados na implementação ou métricas sem relação com o aprendizado e as garantias
do sistema NÃO substituem evidência de qualidade. Métodos, conjuntos de avaliação e limiares
pertencem à especificação e ao plano; esta constituição não impõe TDD nem cobertura arbitrária.

### VII. Execução limitada e falhas transparentes

O sistema DEVE impor limites verificáveis a tempo, chamadas de ferramentas, ciclos de agentes,
volume de dados e tentativas de repetição, conforme os recursos usados por cada fluxo. Valores
e respostas ao atingir os limites DEVEM ser definidos na especificação e no plano.

Falhas DEVEM produzir mensagens compreensíveis e estados que distingam conclusão, interrupção
e resultado parcial. Processamento incompleto NÃO PODE ser apresentado como concluído, nem deixar
gravações parciais disponíveis como conhecimento validado. Recuperação ou repetição DEVE preservar
as regras de autorização, retenção e consistência.

Mensagens e diagnósticos NÃO PODEM expor segredos. A aplicação DEVE permitir identificar a etapa
que falhou com os dados mínimos necessários para diagnóstico, sem conservar conteúdo proibido.

### VIII. Ambientes isolados em contêineres

A configuração do ambiente do projeto, a instalação de suas dependências e a execução de serviços,
builds, testes e avaliações que dependam desse ambiente DEVEM ocorrer em contêineres. É PROIBIDO
instalar dependências ou configurar runtimes e serviços do projeto diretamente no host.

O host PODE ser usado para edição de arquivos, controle de versão e acionamento do runtime de
contêineres. O plano DEVE documentar comandos reproduzíveis e a fronteira entre host e contêiner,
incluindo volumes, configuração e tratamento de segredos. Esta regra não escolhe runtime,
orquestrador de contêineres ou topologia de implantação.

## Escopo vigente e decisões evolutivas

O produto é um assistente pessoal de estudos multiagêntico. As restrições já fornecidas pelo
usuário DEVEM ser carregadas para as próximas especificações:

- Arquivos locais enviados serão somente Markdown; formatos adicionais estão fora do escopo atual.
- Um orquestrador supervisiona o fluxo; um pesquisador busca e extrai fontes web; um tutor usa
  recuperação de conhecimento para ensinar.
- Fontes web passam por uso temporário e seleção explícita antes da ingestão controlada.

Markdown e a composição inicial dos agentes são decisões de escopo vigentes, revisáveis com o
usuário e registradas na especificação. Não exigem, por si só, emenda aos princípios, desde que
sejam preservadas as garantias de confiança, rastreabilidade, controle e responsabilidades.

A especificação DEVE definir jornadas, aceite, fontes consultáveis, estados temporários e
persistidos, descarte, tratamento do histórico e comportamento em falhas. O plano DEVE definir
tecnologias, contratos, regras de processamento, armazenamento, limites, isolamento e estratégia
de testes e avaliações. Frameworks de agentes, modelos, provedores, banco de dados, interface,
parâmetros de chunking, métricas e durações de retenção permanecem decisões futuras; NÃO DEVEM
ser tratados como escolhas aprovadas por esta constituição.

## Fluxo de desenvolvimento e revisão

1. A especificação DEVE ligar cada jornada aos critérios de aceite e aos princípios aplicáveis,
   incluindo insuficiência de evidências, conteúdo hostil, autorização e falhas quando pertinentes.
2. O plano DEVE executar o Constitution Check antes da pesquisa e após o desenho. Cada princípio
   DEVE ter evidência de atendimento ou justificativa explícita de não aplicabilidade à mudança.
   Uma violação não é resolvida apenas por uma justificativa técnica: o desenho DEVE ser corrigido
   ou a constituição formalmente emendada antes da implementação incompatível.
3. As tarefas DEVEM incluir implementação e verificação das garantias no fluxo que as utiliza.
   Segurança, retenção e tratamento de falhas NÃO PODEM ser adiados integralmente para uma fase
   final de polimento. Infraestrutura e instrumentação DEVEM permanecer proporcionais.
4. A revisão de cada entrega DEVE comparar resultado, critérios de aceite e evidências de testes
   e avaliações. Verificações não executadas e riscos remanescentes DEVEM ser declarados; uma
   entrega NÃO PODE ser registrada como validada sem as evidências exigidas para seu escopo.

## Governance

Esta constituição orienta especificações, planos, tarefas, implementação e revisões do StudyForge.
Em caso de conflito entre artefatos do projeto, os princípios aqui definidos prevalecem até uma
emenda aprovada pelo responsável pelo projeto. Suposições técnicas NÃO alteram princípios.

O responsável pelo projeto PODE revisar e complementar o documento conforme o aprendizado do
projeto. Cada emenda DEVE registrar motivo, mudança, impacto em dados e comportamento, necessidade
de migração quando houver e aprovação do responsável. A emenda DEVE atualizar a versão, a data
da última alteração e o Sync Impact Report, além de sincronizar templates e artefatos afetados.

O versionamento segue MAJOR.MINOR.PATCH: MAJOR para remoção ou redefinição incompatível de princípios
ou governança; MINOR para novos princípios, seções normativas ou ampliação material de garantias
compatível com as anteriores; PATCH para esclarecimentos e correções sem mudança semântica.
A data de ratificação original DEVE ser preservada em revisões posteriores.

Toda revisão de especificação, plano ou entrega DEVE verificar conformidade com a versão vigente.
Mudanças de escopo e decisões técnicas ficam nos respectivos artefatos; quando houver atualização
da seção de escopo deste documento, sua versão DEVE refletir o impacto semântico da alteração.

**Version**: 1.0.1 | **Ratified**: 2026-10-28 | **Last Amended**: 2026-10-29

Emenda 1.0.1: correção da interpretação de retenção aprovada pelo usuário em 2026-10-29.
Garantia limitada ao armazenamento local; gate externo G0 retirado. Sem migração de dados.
Plano, especificação, contratos, tarefas, instruções e implementação devem refletir essa correção.
