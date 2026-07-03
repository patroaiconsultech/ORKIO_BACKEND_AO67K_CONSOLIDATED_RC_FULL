# Mapa de Implantação — ORKIO CORE RC2 Runtime Foundation

## Baseline obrigatório

`94ba9246bcd3d2a5c40d42657ae7ca17c80a2826`

O aplicador falha se `git rev-parse HEAD` for diferente.

## Ordem

1. Criar clone limpo no SHA baseline.
2. Extrair este pacote.
3. Executar:

```bash
python tools/apply_shadow_candidate.py --repo /path/to/repo --check
python tools/apply_shadow_candidate.py --repo /path/to/repo --write
python tools/apply_shadow_candidate.py --repo /path/to/repo --write
python tools/validate_shadow_candidate.py --repo /path/to/repo
pytest /path/to/repo/tests/runtime/test_runtime_persistence_shadow.py
```

## Arquivos de produção alterados

Somente por aplicação controlada:

- `runtime/orkio_runtime_foundation/persistence.py`
- `runtime/intent_engine.py`
- `services/governance_service.py`
- `services/capability_service.py`

## Arquivos adicionados de documentação/teste

- `tests/runtime/test_runtime_persistence_shadow.py`
- `architecture/contracts/runtime_persistence_canonical_contract.md`
- `engineering/EPIC002B_CANONICAL_ASSISTANT_MESSAGE_ID_SHADOW_LOCKED.md`
- `engineering/VALIDACAO_LOCAL_EPIC002B.md`
- `adrs/ADR-0003-runtime-persistence-canonical-assistant-message-id.md`

## Proibições

- Não copiar `README.md` para substituir README oficial do repo.
- Não criar `app/config/runtime.py`.
- Não usar shim.
- Não pular SHADOW.
