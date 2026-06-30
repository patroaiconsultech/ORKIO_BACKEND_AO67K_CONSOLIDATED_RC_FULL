# Mission Domain Model

## Definition
Mission is the primary domain entity of ORKIO OS.

A Mission represents a persistent objective that can contain conversations, documents, evidence, hypotheses, decisions, outcomes and learning over time.

## Core Principle
Conversation is transient. Mission is persistent.

## Mission Aggregate

Mission
- Metadata
- State
- Context
- Timeline
- Conversations
- Documents
- Evidence
- Hypotheses
- Decisions
- Planner
- Outcomes
- Learning
- Health

## Initial Kernel
The first Mission Kernel introduces only the minimal domain primitives:

- Mission
- MissionStatus
- MissionStage
- MissionSummary
- MissionContext
- MissionHealth

## Lifecycle
Draft -> Discovery -> Diagnosis -> Planning -> Execution -> Validation -> Learning -> Completed -> Archived

## State Ownership
The LLM never owns the Mission State.
Mission State belongs to ORKIO OS.

## Implementation Note
This document defines the conceptual model. It does not imply persistence, API routes or UI changes in this capability.
