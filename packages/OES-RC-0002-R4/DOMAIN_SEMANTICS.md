# Domain Semantics

## Purpose

Define semantic rules that remove ambiguity between aggregates without introducing new domain concepts.

## Entity / Value Object / Reference Separation

Each aggregate specification must separate:

- Entities: owned domain concepts with identity and lifecycle.
- Value Objects: immutable concepts without independent identity.
- References: stable pointers to concepts owned by other aggregates.

A Reference is not an Entity and does not transfer ownership.

## Evidence Taxonomy

Evidence is a semantic category, not a single mutable entity shared across aggregates.

| Evidence Representation | Owner | Rule |
|---|---|---|
| DecisionEvidence | Decision Authority | Created and governed by Decision. |
| ExecutionEvidence | Runtime Authority | Created and governed by Execution. |
| AuditEvidence | Observability Authority | Registered and governed by Observability. |
| EvidenceReference | Decision Authority | References admissible evidence without ownership transfer. |

## Cross-Aggregate Ownership

- Aggregates own their internal entities.
- Aggregates may reference entities owned by other aggregates through explicit references.
- Aggregates shall not mutate entities owned by other aggregates.
- Promotion across aggregate boundaries requires a capability owned by the destination authority.

## Execution History

Execution history is not an Agent-owned entity.

Agent activity is observed through AuditRecord references governed by Observability Authority.

## Artifact Promotion

An Execution Artifact is not automatically a KnowledgeAsset.

It becomes a KnowledgeAsset only through `PromoteArtifactToKnowledge`, which must invoke a Knowledge Authority governed `CreateKnowledgeAsset` operation.

## Immutability

Immutable domain content may still receive authorized lifecycle metadata transitions.

The immutable part and lifecycle metadata part must be interpreted separately.

## State Machine Rule

Every command-like contract that changes lifecycle state shall have:

- source state;
- target state;
- authority;
- event;
- acceptance condition.

## Capability Semantics

Each capability must define:

- purpose;
- inputs;
- outputs;
- policy or authority;
- dependencies;
- acceptance criteria.

## Canonical Reference Closure

Every cross-aggregate reference used in an Aggregate Specification must be defined in the Canonical Concept Inventory as type `Reference`.

A reference must declare:

- stable Domain ID;
- reference concept name;
- target aggregate;
- owning authority.

Aliases are prohibited. If an Aggregate Specification uses `AuditRecordReference`, the inventory must contain exactly `AuditRecordReference`; `AuditReference` is not a valid implicit alias.

References never transfer ownership and never authorize mutation of the referenced aggregate.
