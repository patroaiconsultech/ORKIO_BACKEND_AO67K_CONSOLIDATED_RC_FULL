# Rollback

## Operacional imediato

```env
ORION_PREMIUM_SHADOW_MODE=true
```

## Desativação total do guard

```env
ORION_DOCUMENT_EVIDENCE_GUARD_ENABLED=false
```

## Rollback de código

1. Restaurar o `main.py` anterior.
2. Remover `services/orion_premium/`.
3. Remover `tests/orion_premium/`.
4. Remover `docs/orion_premium/`.

Não há migração de banco ou schema para reverter.
