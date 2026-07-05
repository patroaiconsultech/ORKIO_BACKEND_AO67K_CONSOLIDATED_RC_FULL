# OES-002 — Engineering Glossary

Version: 0.1-rc-r3
Status: RELEASE CANDIDATE
Owner: Orkio Engineering Office
Approver: Vision Owner + Independent Engineering Auditor
Depends on: OES-001

## Objective
Define the canonical engineering language used by Orkio specifications.

## Scope
Covers normative architectural, delivery, governance, and domain-engineering terms.

## Out of Scope
Does not define every common word used in documentation.

## Terms
- **Architecture:** significant structural decisions shaping organization, integration, governance, validation, and evolution.
- **Baseline:** approved and versioned reference state usable as a normative dependency.
- **Capability:** business or platform ability owned by a functional domain and described with objective, inputs, outputs, policies, dependencies, and acceptance criteria.
- **Canonical:** officially selected representation for a concept within a defined scope.
- **Component:** technical part inside a domain or subsystem.
- **Contract:** versioned public agreement for interaction between domains, services, runtimes, integrations, or clients.
- **Critical Capability:** capability whose failure may materially affect decision quality, security, financial integrity, legal exposure, operational continuity, or user trust.
- **Domain:** coherent area of responsibility with language, ownership, assets, rules, and public contracts.
- **Domain Service:** domain-level behavior that does not naturally belong to a single entity or value object.
- **Entity:** object with stable identity across time.
- **Event:** versioned fact that something relevant happened.
- **Executive Asset:** governed institutional asset used by Orkio.
- **Knowledge Asset:** governed knowledge item with source, classification, version, provenance, and lifecycle state.
- **Non-Destructive Package:** package extractable into target repository without overwriting unrelated or undeclared files.
- **Preflight:** validation step that enumerates paths, compares with target repository, detects collisions, and blocks unsafe extraction.
- **Release Candidate:** package proposed for audit and possible promotion.
- **Service:** runtime implementation exposing behavior through explicit contracts.
- **Source of Truth:** authoritative location for a specific artifact type.
- **Specification:** governed engineering artifact defining what must be built, validated, or followed.
- **Structural Code:** code that changes architecture, public contracts, domain behavior, data model, security model, runtime behavior, or release behavior.
- **Value Object:** object defined by attributes rather than stable identity.

## Acceptance Criteria
- Normative architectural terms used by OES documents have one definition here or a clear external reference.
- Terms distinguish domain, component, service, and contract.
- Canonical and Source of Truth are not used interchangeably.

## Risks
- New documents may introduce undefined normative terms.

## Next Steps
Future OES modules must reference this glossary instead of redefining these terms.

## Revision History
- 0.1-rc: Initial release candidate.
- 0.1-rc-r3: Standardized approval authority with OES-003.
