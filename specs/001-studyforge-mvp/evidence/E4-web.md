# E4 — descoberta e extração HTML

Execução real em contêiner em 2026-10-29: `tests/integration/test_web_external.py`,
opt-in `RUN_EXTERNAL_TESTS=1`, passou em 47,96 s. Brave retornou uma fonte HTML;
o coletor extraiu mais de 1.000 caracteres, o tutor Gemini 3.5 Flash Lite respondeu
com referência temporária e a biblioteca permaneceu vazia até a seleção explícita.
A seleção foi aceita, a conversa encerrada e a ingestão autorizada concluiu.
O teste utilizou schema PostgreSQL isolado, removido ao terminar.

Nenhuma chave, corpo HTML, pergunta real ou fonte não selecionada foi registrada
nesta evidência. Uma consulta bem-sucedida comprova conectividade e o caminho
integrado; não mede cobertura geral da busca nem taxa de extração na web.

Regressão local: `test_safe_fetcher.py`, `test_web_destinations.py`,
`test_safe_fetch.py`, `test_html_extraction.py` e `test_html_corpus.py`.
Cobrem IP efetivamente conectado, DNS misto, destinos privados, redirects,
rebinding, Host/SNI/TLS, proxies ignorados e gzip expansivo rejeitado antes de
descompressão. Não existe fallback de transporte que faça nova resolução DNS.
Fixtures HTML verificam estrutura, tabelas, código e remoção de boilerplate.

Limitação deliberada e provisória: solicita HTML sem compressão e rejeita respostas
comprimidas. Não houve necessidade demonstrada de trocar Brave ou o extrator;
alternativas não foram adicionadas. O orçamento da pesquisa agora permite devolver
fontes já obtidas quando o prazo se esgota, sinalizando falha parcial.
