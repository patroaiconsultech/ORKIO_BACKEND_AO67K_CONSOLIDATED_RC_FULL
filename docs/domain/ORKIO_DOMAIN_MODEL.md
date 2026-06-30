# ORKIO Domain Model

## Purpose

The ORKIO Domain Model defines the conceptual language and relationships that govern the Cognitive Operating System (COS).

It does not describe implementation details, framework choices, APIs, database tables, frontend components, or LLM providers.

The purpose of this document is to answer:

> What are the stable domain concepts of the ORKIO OS, and how do they relate?

## Foundational Definition

The ORKIO OS is a domain-driven Cognitive Operating System (COS) that uses AI to conduct Missions while preserving context, evidence, governance, and traceability across the decision lifecycle.

## Core Domain Principle

> Conversation is transient. Mission is persistent.

A conversation is a channel of interaction. A Mission is the persistent domain entity that organizes purpose, context, evidence, decisions, outcomes, and learning.

## Concept Map

```text
Strategic Intent
        │
        ▼
Mission
        │
        ├── Context
        ├── State
        ├── Health
        ├── Timeline
        ├── Conversations
        ├── Documents
        ├── Evidence
        ├── Hypotheses
        ├── Decisions
        ├── Planner
        ├── Outcomes
        └── Learning
```

## Domain Concepts

### Strategic Intent

A Strategic Intent represents an organizational purpose that may generate multiple Missions.

Example:

> Digitize real estate feasibility analysis.

A Strategic Intent is broader than a Mission. It defines why Missions exist.

### Mission

A Mission is the aggregate root of the ORKIO OS domain.

It represents a persistent objective being conducted over time.

A Mission may contain conversations, documents, evidence, hypotheses, decisions, outcomes, timeline events, and learning projections.

### Conversation

A Conversation is an interaction channel and event stream associated with a Mission.

It is not the primary source of truth for the system. It is one way in which a Mission receives input and produces responses.

### Document

A Document is an artifact attached to a Mission.

Documents may produce Evidence, support Hypotheses, influence Decisions, or become part of the Mission Context.

### Evidence

Evidence is an observed artifact or verified information used to support reasoning.

Evidence must be distinguished from Hypothesis, Opinion, and Assumption.

### Hypothesis

A Hypothesis is a provisional interpretation that helps the Mission advance under uncertainty.

A Hypothesis may be confirmed, revised, or rejected as new Evidence emerges.

### Decision

A Decision is an explicit choice accepted by a human or authorized governance process within a Mission.

The ORKIO OS may recommend, structure, and critique decisions, but the human remains responsible for the decision.

### Outcome

An Outcome is the result or consequence of actions taken within a Mission.

Outcomes provide feedback for Learning.

### Learning

Learning is a derived projection from Mission events, decisions, outcomes, and feedback.

Learning does not override the Mission state. It informs future reasoning and recommendations.

### Mission Health

Mission Health is a value object that summarizes the condition of a Mission.

It may include progress, confidence, risks, blockers, next action, and executive summary.

### Workspace

A Workspace is an organizational environment where Missions, agents, documents, and users collaborate.

### Organization

An Organization is the tenant or institutional owner of Workspaces and Missions.

### Agent

An Agent is an operational or cognitive participant that can contribute to a Mission under governance constraints.

Agents do not own Mission state.

## Ownership Rules

- Every persistent artifact belongs to exactly one Mission.
- Conversations belong to Missions.
- Documents belong to Missions.
- Evidence belongs to Missions.
- Hypotheses belong to Missions.
- Decisions belong to Missions.
- Outcomes belong to Missions.
- Learning is derived from Mission events.
- The LLM never owns Mission state.

## Non-Goals

This document does not define:

- database schema;
- API payloads;
- frontend UI;
- LLM prompts;
- persistence strategy;
- event sourcing implementation.

Those decisions may evolve later, but they must remain compatible with this domain model.

## Architecture Impact

Future capabilities must preserve the integrity of this model.

If a new implementation introduces or redefines a Domain Concept, the Domain Model and Ubiquitous Language must be updated before or together with the implementation.
