# CEF-001A-P1 — Orion Capability Routing & Evidence Contract

Data: 13 de julho de 2026
Status: PATCH_PREVIEW_VALIDATED_LOCALLY
Escopo: backend only
Banco: sem alteração
Migration: não
Frontend: não alterado

## 1. Objetivo

Corrigir quatro divergências comprovadas no CEF-001A-P0:

1. destino explícito `Orion` não pode converter toda solicitação em `direct_agent_message`;
2. restrições negativas precisam vencer inferência de PR, proposta, escrita, merge e deploy;
3. recibos sem evidência de ferramenta não podem declarar `executed`;
4. AO-17 só pode ser selecionado quando o turno atual pedir explicitamente auditoria UX.

## 2. Arquivos novos

- `runtime/orion_capability_policy.py`
- `runtime/execution_evidence_contract.py`
- `tests/test_cef001a_orion_capability_routing.py`
- `tests/test_cef001a_execution_evidence_contract.py`
- `docs/audits/2026-07/CEF001A_P1_ORION_CAPABILITY_ROUTING.md`

## 3. Arquivos ajustados

- `runtime/intent_engine.py`
- `routes/internal/orion_internal.py`
- `main.py`

## 4. Contrato do patch

### 4.1 Destino explícito

O destino explícito continua definindo autoria e ownership.

Ele não define sozinho a capability.

Fluxo novo:

```text
destino explícito Orion
→ classificar o pedido atual
→ pedido técnico read-only?
  → sim: capability platform_self_audit, owner Orion
  → não: direct_agent_message
```

### 4.2 Restrições negativas

São avaliadas antes de inferência baseada em substring.

Exemplos:

```text
sem proposta
sem escrita
não abra PR
não faça merge
não faça deploy
read-only
somente leitura
```

A sigla `PR` deixa de ser inferida a partir de `pr` dentro da palavra `proposta`.

### 4.3 Evidência

Um receipt só pode permanecer com `status=executed` quando possuir:

```text
tool_used
tool_run_id
repository
branch
commit
operation
result_digest
started_at
finished_at
write_executed
```

Receipts estáticos passam a:

```text
status=simulated
verification_level=trace_lite
evidence_verified=false
execution_claim=not_verified
```

### 4.4 AO-17

Palavras genéricas como `premium`, `interface`, `onboarding`, `mobile` ou `PWA`
não são suficientes.

AO-17 exige verbo explícito de ação UX no turno atual e é bloqueado quando o turno
está claramente focado em CEF-001, ownership, capability registry ou mapa de código.

## 5. Impacto arquitetural

- `AppConsole.jsx`: 0 linhas alteradas.
- `main.py`: lógica reduzida; o matcher UX foi extraído para módulo dedicado.
- nenhuma migration;
- nenhuma escrita;
- nenhum novo endpoint;
- nenhum novo fast-path;
- nenhuma alteração de tenant;
- nenhuma alteração de auth;
- nenhuma alteração de SSE.

## 6. Testes locais

```text
python -m py_compile   runtime/orion_capability_policy.py   runtime/execution_evidence_contract.py   runtime/intent_engine.py   routes/internal/orion_internal.py   main.py

python -m pytest -q   tests/test_cef001a_orion_capability_routing.py   tests/test_cef001a_execution_evidence_contract.py
```

Resultado local:

```text
py_compile: PASS
pytest: 12 passed
```

## 7. Riscos

1. `intent_engine.py` possui alta densidade de regras e precisa de regressão ampliada no clone atual;
2. o artifact Backend 34 pode divergir do `origin/main` atual;
3. mudar receipts de `executed` para `simulated` pode revelar dependências visuais ocultas;
4. o patch não cria um repository reader real; apenas deixa o roteamento pronto e honesto;
5. o patch não habilita write, PR, merge ou deploy.

## 8. Rollback

Reverter os três arquivos ajustados e remover os dois módulos e testes novos.

Nenhum rollback de banco é necessário.

## 9. Critério de GO

- patch aplicado sobre clone limpo do `origin/main`;
- nenhum conflito silencioso;
- testes novos verdes;
- testes auth/tenant/threads/SSE existentes verdes;
- import real do backend;
- route count sem alteração inesperada;
- smoke do Orion:
  - mensagem casual permanece direta;
  - pedido de mapa read-only chega à capability;
  - ownership permanece Orion;
  - receipts sem ferramenta aparecem como trace_lite;
  - documento com palavras UX não desvia para AO-17;
- diff revisado;
- rollback provado.

## 10. Governança

```text
write_executed=false
commit_executed=false
merge_executed=false
deploy_executed=false
migration_executed=false
execution_allowed=false
human_approval_required=true
```
