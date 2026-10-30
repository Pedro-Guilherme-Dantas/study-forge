# Regressão de segurança — 2026-10-29

Suíte final executada na imagem de produto: **122 aprovados, 2 externos opt-in
separados**, incluindo controles localhost/Host/Origin/CSRF, limites de corpo,
erros sanitizados, SSRF/IP pinado, gzip rejeitado, admissão/cancelamento, autorização
e publicação atômica. As duas integrações externas também passaram separadamente.

Inspeção do ambiente efetivo: app read-only, /tmp em tmpfs limitado, sem core dump,
logging none, somente 127.0.0.1:8000 publicado e banco sem porta no host.
Inspeção dentro do contêiner comparou os valores reais das duas chaves com todos
os arquivos do bundle: nenhum encontrado. Só o resultado booleano foi impresso.
O cache de avaliação está ausente da imagem. Nenhum ambiente/chave foi expandido
para saídas de ferramenta ou documentos.

MarkdownView usa renderização Markdown sem HTML bruto e bloqueia imagens remotas;
links passam por allowlist http(s). A revisão de código confirma esse controle;
a matriz visual de renderização/acessibilidade ainda não está integralmente
ensaiada. Não apresentar esta regressão como auditoria de segurança exaustiva.

Retenção: `test_selection_retention.py` inspeciona tabelas e arquivos graváveis após
resposta derivada de fonte B não selecionada. O marcador exclusivo evita colisão
aleatória do embedding fixture; o teste mede retenção, não relevância semântica.
Logs capturados e erros inesperados não contêm o marcador. Sessão fechada rejeita
callback antigo; reinício restaura somente biblioteca. Veja E0-retention.md.
