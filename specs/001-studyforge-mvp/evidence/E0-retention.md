# E0 — retenção local e envio externo

Revisão aprovada pelo usuário em 2026-10-29: **G0 externo retirado**. A exigência é que conversas e fontes não selecionadas não fiquem persistidas localmente. Não se exige comprovante de retenção zero ou descarte remoto nas APIs de IA e busca. Provedores aplicam suas próprias políticas, informadas na interface.

Permanecem: chat e fontes temporárias apenas em RAM; descarte ao encerrar/reiniciar; nenhuma persistência indireta em banco, logs, traces, checkpoints ou arquivos locais; seleção explícita para guardar fontes. Credenciais no backend e verificação de integrações continuam necessárias.

O código de comprovante foi removido. Gemini Developer API pode usar GEMINI_API_KEY; Vertex usa projeto/região e credenciais correspondentes. Busca exige SEARCH_API_KEY. Ausência de configuração gera erro compreensível, sem chamadas de rede. Nenhuma chave real foi fornecida e nenhuma chamada externa foi executada nesta revisão.

## Verificação posterior no ambiente efetivo — 2026-10-29

Credenciais configuradas pelo usuário, sem impressão ou leitura de seus valores.
As integrações reais Gemini/Brave passaram separadamente. Inspeção do Docker em
execução confirmou app com filesystem somente leitura, `/tmp` em tmpfs de 32 MiB,
logging `none` em app e banco, única porta do app vinculada a 127.0.0.1:8000 e
nenhuma porta de banco publicada. Não foi consultado o ambiente dos contêineres.

`test_selection_retention.py` inspeciona todas as tabelas do schema de ensaio,
logs capturados e arquivos graváveis após recuperação e resposta derivada de B
não selecionada, enquanto A é ingerida. B permanece ausente. Os testes de sessão
verificam descarte e callback atrasado rejeitado por epoch; a jornada integrada
reinicia a aplicação e conserva somente a biblioteca. Traces/checkpoints de
conversa não são configurados no grafo; LangSmith fica desativado no Compose.

O cache de embeddings do benchmark é uma exceção explícita para o corpus público
selecionado pelo usuário para avaliação, separado do runtime e excluído de Git e
build. Não recebe fontes de pesquisa ou conversas do produto. Estes testes são
evidência delimitada ao ambiente/container e caminhos exercitados; não prometem
apagamento de cópias dos provedores nem uma inspeção forense do host inteiro.

A exigência anterior de comprovar retenção do fornecedor foi uma interpretação mais restritiva do requisito, corrigida por este esclarecimento. Evidências anteriores que citam G0 bloqueado são históricas e não representam uma pendência atual.
