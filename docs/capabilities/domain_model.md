# CP-003 — Domain Model Foundation

## Capability

Domain Model

## Objective

Establish the first explicit conceptual domain model for the Cognitive Operating System (COS), centered on Mission as the aggregate root.

This capability documents the stable concepts that guide future implementation without introducing runtime, persistence, APIs, services, or frontend changes.

## Core

Governance Core / Cognitive Core

## Domain Concepts

- Strategic Intent
- Mission
- Conversation
- Evidence
- Hypothesis
- Decision
- Outcome
- Learning
- Mission Health
- Workspace
- Organization
- Agent

## Architecture Principles

- Conversation is transient. Mission is persistent.
- Mission is the aggregate root.
- Conversation is an event stream.
- Memory is derived from Mission events.
- The LLM never owns Mission state.
- The Domain owns the Architecture. The Architecture owns the Runtime. The Runtime orchestrates the Models.

## Scope

This patch is documentation and contract-test only.

## Out of Scope

- Runtime implementation
- Persistence
- Database migrations
- API endpoints
- Frontend
- LLM orchestration
- Planner implementation
- Memory implementation

## Acceptance Criteria

- Domain Model document exists.
- Required domain concepts are defined.
- Mission is declared as aggregate root.
- Conversation is explicitly described as an interaction channel and event stream.
- Persistent artifacts are attached to Mission.
- Runtime remains untouched.
