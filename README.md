# ORKIO OS 2 — Phase 2A Microkernel + Knowledge Layer

## Objective

This package introduces an isolated Cognitive Microkernel and a first Knowledge Ingestion Layer for Orkio OS 2.

It does **not** modify production routes.

## Included

- `app/cognitive`: microkernel, contracts, plugin registry, event bus, envelope builder
- `app/cognitive/plugins`: core starter plugins for intent, policy, risk, runtime
- `app/knowledge`: ingestion, classifier, schema, source registry, summarizer, store, graph
- `tests`: unit tests for cognitive and knowledge modules
- `docs`: operational ADR
- `patches`: validation checklist

## Safety posture

Default mode is `shadow`.

The kernel:
- does not call OpenAI
- does not touch database
- does not alter `/api/chat`
- does not alter `/api/chat/stream`
- does not alter auth
- does not alter frontend
- does not execute production actions

## Suggested validation

```bash
python -m compileall app tests
python -m pytest -q
```

## Recommended branch

```bash
git checkout -b feature/orkio-os-2-phase-2a-microkernel
```

## AO-01 Verdict

GO for branch integration.
NO-GO for direct production enforcement.
