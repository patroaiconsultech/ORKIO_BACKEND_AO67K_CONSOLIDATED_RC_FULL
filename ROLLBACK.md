# Rollback

Rollback imediato:

```env
ORKIO_VISION_PIPELINE_ENABLED=false
```

Isso mantém o bloqueio seguro para imagens.

Rollback completo:
1. restaurar `services/file_upload_indexing_service.py`;
2. restaurar `services/orion_premium/evidence_guard.py`;
3. remover `vision_gateway.py` e `evolution_hub.py`;
4. remover os testes Premium 2.

Não há migração de banco nem alteração de schema.
