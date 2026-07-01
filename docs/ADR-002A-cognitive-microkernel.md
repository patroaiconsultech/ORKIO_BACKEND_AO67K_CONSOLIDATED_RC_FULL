# ADR-002A — Cognitive Microkernel + Knowledge Layer

## Status

Accepted for branch implementation.

## Context

Orkio OS 2 needs a decision layer that can evolve without turning into a new monolith.

## Decision

Implement a microkernel with five responsibilities:

1. Receive
2. Evaluate
3. Plan
4. Dispatch
5. Observe

All domain-specific intelligence must live in plugins.

## Knowledge Layer

GPT conversations and strategic documents must be ingested as structured knowledge, not appended as raw prompt context.

Knowledge is separated into:

1. Canonical memory
2. Strategic history
3. Raw source archive

## Consequences

Positive:
- safer evolution
- easier rollback
- reusable by PatroAI verticals
- marketplace-ready architecture

Negative:
- more upfront structure
- requires governance discipline

## Production Rule

The Phase 2A package must remain isolated until Shadow Mode integration is explicitly approved.
