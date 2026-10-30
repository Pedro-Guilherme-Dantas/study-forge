# Contratos HTTP e cliente

Em 2026-10-29, a suíte completa passou com 121 testes. A comparação com o OpenAPI
revisado cobre paths, operationIds, campos, literais/enums e constraints aninhadas
de tamanho, limites numéricos, pattern, format e additionalProperties.

Corrigidos limites positivos, epoch não negativo e documentação de URLs;
multipart de upload, autenticação cookie/CSRF e envelopes sanitizados de erro agora
aparecem no OpenAPI gerado. Readiness mantém seu contrato HealthInfo no 503.
Idempotency-Key de seleção está declarado como header com limites de tamanho.

O cliente TypeScript distingue citações de biblioteca e temporárias por scope,
com snapshot_hash obrigatório nas temporárias; inclui reason_code e os detalhes
sanitizados de erro. O build executa typecheck e Vite. Não existe geração automática
de tipos do OpenAPI; a comparação de tipos continua explícita e revisável.
