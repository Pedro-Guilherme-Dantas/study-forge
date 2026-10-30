# Diagnóstico de cota de embeddings — 2026-10-29

Após relato do usuário, uma única chamada direta de diagnóstico foi executada no
backend com texto autoral, sem usar materiais ou conversas pessoais. Resultado
observado: ClientError 429, quotaId
`EmbedContentRequestsPerDayPerUserPerProjectPerModel-FreeTier`, quotaValue 1000,
modelo configurado gemini-embedding-001 e RetryInfo de 22985 segundos no instante
do diagnóstico. Valores de chave e mensagens brutas do SDK não foram exibidos.

A falha é de cota diária do serviço de embeddings, não do modelo de geração.
Trocar o tutor por 3.1 não resolve essa condição. Os experimentos anteriores usaram
o mesmo projeto e contribuíram para o consumo; não foi medido o consumo exclusivo
de cada origem. A espera informada pelo provedor é uma indicação, não garantia de
disponibilidade em horário exato. Não houve alteração de conta, cobrança ou modelo.

Correções aplicadas:

- Respostas 429 agora geram PROVIDER_QUOTA_EXCEEDED com mensagem específica de
  cota diária ou limite de uso, sem expor payload de erro do fornecedor.
- Recuperação sem nenhum chunk publicado compatível e sem fonte temporária
  retorna conjunto vazio antes de pedir embedding. O tutor pode informar falta de
  evidência e oferecer pesquisa sem uma chamada vetorial inútil.
- Testes cobrem cotas diária/minuto em embeddings/geração e ausência de chamada
  externa na recuperação vazia. A integração real com embeddings continua
  condicionada à liberação da cota; o patch não restaura recursos do provedor.

Validação: 16 testes direcionados aprovados; regressão completa com 130 testes
aprovados, 2 externos opt-in separados, e build/typecheck em contêiner aprovado.
