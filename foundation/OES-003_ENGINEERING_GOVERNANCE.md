# OES-003 — Engineering Governance

Version: 0.1-rc-r3
Status: RELEASE CANDIDATE
Owner: Orkio Engineering Office
Approver: Vision Owner + Independent Engineering Auditor
Depends on: OES-001, OES-002

## Objective
Define how engineering decisions, reviews, approvals, baselines, and changes are governed.

## Scope
Applies to specification modules, packages, structural code, release candidates, audits, and baseline promotion.

## Out of Scope
Company legal governance, financial approvals, employment policy, and production incident response.

## Roles
- **Vision Owner:** owns product intent, strategic priorities, and final human scope approval.
- **Architecture & Engineering Lead:** owns specifications, risks, structure, coherence, and remediation proposals.
- **Independent Engineering Auditor:** audits safety, ambiguity, consistency, integrity, and readiness.
- **Repository Maintainer:** applies approved packages, validates repository state, records evidence, and commits.

## Artifact States
DRAFT → REVIEW → RELEASE CANDIDATE → APPROVED → BASELINE

## Approval Authority
- Promotion from RELEASE CANDIDATE to APPROVED requires both:
  - explicit Vision Owner approval; and
  - GO from the Independent Engineering Auditor.
- The Repository Maintainer executes the repository promotion only after both approvals are recorded.
- Rejection by either authority returns the package to REVIEW or requires a new release-candidate revision.
- Rejected release candidates must not become normative dependencies.

## Atomic Baseline Promotion
- Documents delivered in the same release candidate are promoted as one atomic package unless package metadata explicitly declares otherwise.
- OES-001, OES-002, OES-003, and OES-004 in this package must be approved and baselined together.
- Partial baseline promotion of mutually dependent documents is not allowed.

## Approval Rules
- DRAFT documents may not be normative dependencies.
- RELEASE CANDIDATES require independent audit.
- APPROVED status requires Vision Owner approval and Independent Engineering Auditor GO.
- BASELINE promotion requires no unresolved P0/P1 findings.
- P2 findings require remediation, documented rationale, or an approved follow-up plan before baseline.

## Change Policy
Baseline changes must declare what changes, why, affected artifacts, compatibility, validation, and rollback.

## Acceptance Criteria
- Roles and artifact states are clear.
- Baseline dependency rules are explicit.
- Audit severity handling is explicit.

## Risks
- Governance may slow delivery if applied without proportionality.

## Next Steps
Use this governance model in all future OES release candidates.

## Revision History
- 0.1-rc: Initial release candidate.
- 0.1-rc-r3: Standardized approval authority, rejection flow, and atomic package promotion.
