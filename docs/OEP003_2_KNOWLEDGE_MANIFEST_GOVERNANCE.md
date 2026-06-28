# OEP-003.2 — Knowledge Manifest + Governance Check

## Objetivo

Consolidar o Knowledge Layer com manifesto e validação de governança.

## Garantias

- `proposal_only = true`
- `write_executed = false`
- `human_approval_required = true`

## Escopo preservado

Este patch não toca chat, realtime, Team, voice, frontend, auth ou banco.

## Teste

```bash
PYTHONPATH=. python -m py_compile evolution/*.py tests/oep003_2_knowledge_manifest_governance_smoke.py
PYTHONPATH=. python tests/oep003_2_knowledge_manifest_governance_smoke.py
```

Resultado esperado:

```txt
OEP003_2_KNOWLEDGE_MANIFEST_GOVERNANCE_PASS
```
