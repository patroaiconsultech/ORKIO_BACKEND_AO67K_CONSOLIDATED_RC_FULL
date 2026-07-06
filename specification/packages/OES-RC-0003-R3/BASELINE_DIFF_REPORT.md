# BASELINE_DIFF_REPORT — OES-RC-0003-R3

## Objective

Compare the rejected OES-RC-0003 package against the approved OES-005 baseline and document why R1 was reconstructed instead of patched manually.

## Inputs

- Baseline: OES-RC-0002-R4 / OES-005 Canonical Domain Model
- Baseline SHA-256: `4273278F9786F1E9F0EE86CB4F5D8577B47BA76C44866C16676C85738A66A20A`
- Rejected package: OES-RC-0003
- Rejected package SHA-256: `5F54504C129F15FF94B3052E600C2871EE0C03EB076A361C8C220C0712F6D265`

## Summary

| Metric | Result |
|---|---:|
| Expected capabilities from OES-005/R4 | 56 |
| Capability IDs found in rejected OES-006/RC | 57 |
| Missing expected IDs in rejected RC | 12 |
| Extra IDs in rejected RC | 13 |
| Same ID with different name | 21 |

## Missing IDs in rejected RC

- CAP-IDN-001
- CAP-IDN-002
- CAP-IDN-003
- CAP-IDN-004
- CAP-IDN-005
- CAP-IDN-006
- CAP-IDN-007
- CAP-IDN-008
- CAP-IDN-009
- CAP-AGT-006
- CAP-EXE-007
- CAP-GOV-009

## Extra IDs in rejected RC

- CAP-ORG-001
- CAP-ORG-002
- CAP-ORG-003
- CAP-RULE-001
- CAP-RULE-002
- CAP-RULE-003
- CAP-RULE-004
- CAP-RULE-005
- CAP-RULE-006
- CAP-RULE-007
- CAP-RULE-008
- CAP-RULE-009
- CAP-RULE-010

## Renamed / Reused IDs in rejected RC

- CAP-KNW-001: expected `CreateKnowledgeAsset` but found `CreateKnowledge`
- CAP-KNW-002: expected `ValidateKnowledgeAsset` but found `ValidateKnowledge`
- CAP-KNW-003: expected `ApproveKnowledgeAsset` but found `ApproveKnowledge`
- CAP-KNW-004: expected `OperationalizeKnowledgeAsset` but found `PublishKnowledge`
- CAP-KNW-005: expected `ArchiveKnowledgeAsset` but found `ArchiveKnowledge`
- CAP-AGT-001: expected `CreateAgent` but found `RegisterAgent`
- CAP-AGT-002: expected `ApproveAgent` but found `ConfigureAgent`
- CAP-AGT-003: expected `BindCapability` but found `ActivateAgent`
- CAP-AGT-004: expected `ActivateAgent` but found `SuspendAgent`
- CAP-AGT-005: expected `SuspendAgent` but found `ArchiveAgent`
- CAP-DEC-002: expected `AttachEvidence` but found `ValidateDecision`
- CAP-DEC-003: expected `SubmitDecisionReview` but found `ReviewDecision`
- CAP-EXE-002: expected `AuthorizeExecution` but found `StartExecution`
- CAP-EXE-003: expected `StartExecution` but found `CoordinateExecution`
- CAP-GOV-002: expected `SubmitPolicyReview` but found `ReviewPolicy`
- CAP-GOV-004: expected `RejectPolicy` but found `PublishPolicy`
- CAP-GOV-005: expected `PublishPolicy` but found `SupersedePolicy`
- CAP-GOV-006: expected `SupersedePolicy` but found `DelegateAuthority`
- CAP-GOV-007: expected `DelegateAuthority` but found `RevokeDelegation`
- CAP-GOV-008: expected `RevokeDelegation` but found `ArchivePolicy`
- CAP-OBS-005: expected `ArchiveEvidence` but found `ArchiveAuditRecord`

## Decision

R1 is reconstructed from OES-005/R4 instead of being manually patched from the rejected RC.
