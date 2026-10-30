> Atualização 2026-10-29: referências abaixo ao bloqueio externo G0 são históricas. O usuário limitou a garantia ao armazenamento local e retirou o gate. Resultados de testes anteriores permanecem como executados; integrações reais ainda não foram verificadas.

# Verificações locais de recuperação e agentes

Em 2026-10-29, `python -m evals.run` foi executado em contêiner com 12 documentos e 12 perguntas próprios. Nos 11 casos respondíveis, Recall@3/5/8 foi 1,0 e MRR médio foi 0,9545. O caso sem resposta foi separado. Perfil: fixture-hash-v1:768. **Esse baseline lexical controlado não mede Gemini, embeddings reais, generalização ou qualidade pedagógica.**

`python -m evals.agents` executou 12 cenários rotulados, correspondentes a 17 verificações parametrizadas aprovadas. Cobre citações, lacunas, ausência de suporte, campos de autoridade indevidos, espera/recusa, negação, descarte, seleção e limites. Critérios de revisão humana estão em backend/evals/agent_cases.jsonl. A revisão semântica com respostas reais continua pendente.

Testes adicionais verificaram pesquisa vazia, fonte parcial, excesso de quota e G0 bloqueado, todos sem falsa conclusão; seleção concorrente, fechamento antes/depois do commit e falha ao agendar depois da seleção foram verificados com PostgreSQL real e providers de fixture.

As provas HTTP de SSRF usam resolução/streams controlados. Foi observado IP aprovado no connect_tcp, Host/SNI originais e contexto TLS com verificação de certificado. Nenhuma conexão pública real é alegada. HTML comprimido é rejeitado, sem descompactação ilimitada. Busca/HTML reais, credenciais e qualidade dos modelos continuam abertas.

Os locks de entrega e as imagens foram efetivamente construídos; o Dockerfile executa checagem TypeScript e Vite. Formatação foi executada em contêineres com Prettier 3.9.10 e Ruff 0.17.3; nenhuma instalação foi feita no host.

Rodada final completa: `docker compose build --quiet app` concluiu com sucesso (typecheck e Vite no Dockerfile); `docker compose run --rm --no-deps -e TEST_DATABASE_URL=... app pytest -q -p no:cacheprovider` retornou **94 passed, 14 warnings in 5.73s**. Os warnings são depreciações transitivas de LangSmith/Google SDK, sem falha de teste. Os testes foram executados na imagem final, sem mount do código. Após subir essa imagem, a biblioteca pessoal continuou com zero materiais.
