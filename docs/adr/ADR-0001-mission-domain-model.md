# ADR-0001 — Mission-Centered Domain Model

## Status

Accepted

## Context

The ORKIO OS is evolving from a chat-oriented AI platform into a domain-driven Cognitive Operating System (COS).

A chat-centered architecture creates risk because it treats the conversation as the primary object. The ORKIO OS requires a persistent object that can survive across channels, documents, decisions, agents, and outcomes.

## Decision

Mission is the aggregate root of the ORKIO OS domain.

Conversation is transient and belongs to Mission.

Every persistent artifact belongs to exactly one Mission.

The LLM never owns Mission state. Mission state is owned by the runtime and governed by the ORKIO OS.

## Consequences

Positive:

- The platform becomes channel-agnostic.
- Future voice, email, API, document and agent interactions can all attach to the same Mission.
- Cognitive components can operate on Mission instead of raw chat history.
- Mission state remains auditable and model-independent.

Trade-offs:

- More discipline is required when introducing new domain concepts.
- Chat cannot be treated as the complete source of truth.
- Future persistence must respect Mission ownership rules.

## Scope

This ADR establishes conceptual architecture only. It does not mandate a specific database, API, event store, or runtime implementation.
