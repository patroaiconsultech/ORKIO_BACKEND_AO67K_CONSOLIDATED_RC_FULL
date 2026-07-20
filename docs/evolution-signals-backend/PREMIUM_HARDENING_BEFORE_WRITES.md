# Melhorias premium antes de habilitar escritas

Não bloqueiam o rollout readonly:

1. constraint/idempotência para avaliações duplicadas;
2. idempotency key nos dois POSTs;
3. preenchimento real e validado de `evidence_refs_json`;
4. persistência da janela real de cada fórmula;
5. fórmula global com pesos versionados;
6. teste PostgreSQL real com duas réplicas;
7. política de retenção de snapshots;
8. rate limit administrativo para POSTs;
9. observabilidade estruturada por request ID;
10. teste de concorrência e retry.

Até essas melhorias receberem auditoria:

```text
EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED=false
EVOLUTION_AGENT_EVAL_WRITE_ENABLED=false
```
