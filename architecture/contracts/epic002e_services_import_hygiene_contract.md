# Contrato — EPIC-002E Services Import Hygiene

## Autoridade

Este EPIC não cria autoridade nova.

## Regra

O import de `capability_service` dentro de `services/governance_service.py` deve apontar para o namespace real:

`services.capability_service`

e não para o namespace legado:

`app.services.capability_service`

## Fail-closed

O aplicador falha se:

- o alvo não existir;
- o módulo de destino não existir;
- a substituição deixar import legado no alvo.

## Proibições

- shim;
- fallback vazio;
- mudança de lógica de negócio;
- alterações fora do alvo.
