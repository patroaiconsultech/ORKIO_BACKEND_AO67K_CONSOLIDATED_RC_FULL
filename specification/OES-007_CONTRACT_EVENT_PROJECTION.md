# OES-007 — Contract and Event Projection

**Title:** Contract and Event Projection  
**Version:** 0.1-rc-r1  
**Status:** Release Candidate  
**Owner:** Chief Architecture & Engineering Officer (AO-01)  
**Approver:** Vision Owner + Independent Engineering Auditor  
**Release Candidate:** OES-RC-0004-R1  

## Dependencies

- OES-001 — Engineering Constitution (Baseline)
- OES-002 — Engineering Glossary (Baseline)
- OES-003 — Engineering Governance (Baseline)
- OES-004 — Engineering Delivery Standard (Baseline)
- OES-005 — Canonical Domain Model (Baseline / OES-RC-0002-R4)
- OES-006 — Capability Catalog (Baseline / OES-RC-0003-R3)
- OES-006 SHA-256: `C17580C10C773B5D7917D35DE6A90C62919CA14A2670E4222AE971492CC3FC64`

## Objective

Define the normative command-contract and domain-event projection for ORKIO, derived deterministically from the 56 capabilities approved in OES-006.

OES-007 specifies how each approved capability becomes:

1. exactly one primary command contract;
2. exactly one primary success event;
3. a minimum envelope for idempotency, causation, correlation and auditability;
4. a traceable connection back to OES-006 and OES-005.

## Scope

This release candidate is **specification-only**.

It does not introduce runtime code, database migration, API route, infrastructure change, queue implementation or persistence implementation.

## Non-goals

- Do not implement handlers.
- Do not add database tables.
- Do not expose external API endpoints.
- Do not alter existing runtime behavior.
- Do not create new domain concepts outside OES-005/OES-006.
- Do not introduce references outside the approved OES-006 vocabulary.

## Canonical Vocabulary Closure

The following reference vocabulary is inherited from OES-006 and is closed for this release:

- `OrganizationReference`
- `WorkspaceReference`
- `KnowledgeAssetReference`
- `AgentReference`
- `CapabilityReference`
- `ConversationReference`
- `DecisionReference`
- `ExecutionReference`
- `PolicyReference`
- `AuditRecordReference`
- `EvidenceReference`

## Projection Rules

| Rule | Requirement |
|---|---|
| Contract coverage | Every OES-006 capability MUST have exactly one primary command contract. |
| Event coverage | Every OES-006 capability MUST have exactly one primary success event. |
| Idempotency | Every command contract MUST require an `idempotency_key`. |
| Causation | Every command/event envelope MUST carry `causation_id`. |
| Correlation | Every command/event envelope MUST carry `correlation_id`. |
| Actor traceability | Every command/event envelope MUST carry `actor_agent_reference` as `AgentReference`. |
| Auditability | Every success event MUST be eligible for `AuditRecordReference` correlation. |
| Reference closure | Reference fields MUST be drawn only from the OES-006 vocabulary. |
| Failure handling | Rejected commands MUST NOT emit primary success events. |
| Runtime isolation | This RC MUST remain specification-only. |

## Command Contract Envelope

Each command contract uses the following minimum envelope:

```json
{
  "message_id": "string",
  "schema_version": "0.1-rc-r1",
  "capability_id": "CAP-XXX-000",
  "command_contract_id": "CON-XXX-000",
  "idempotency_key": "string",
  "issued_at": "RFC3339 timestamp",
  "actor_agent_reference": "AgentReference",
  "correlation_id": "string",
  "causation_id": "string",
  "payload": {}
}
```

## Domain Event Envelope

Each primary success event uses the following minimum envelope:

```json
{
  "event_message_id": "string",
  "schema_version": "0.1-rc-r1",
  "capability_id": "CAP-XXX-000",
  "event_id": "EVT-XXX-000",
  "occurred_at": "RFC3339 timestamp",
  "aggregate_root": "DOM-000 Name",
  "actor_agent_reference": "AgentReference",
  "correlation_id": "string",
  "causation_id": "string",
  "audit_record_reference": "AuditRecordReference",
  "produced_references": []
}
```

## Domain Coverage

| Domain | Count |
|---|---:|
| Identity Domain | 9 |
| Knowledge Domain | 5 |
| Agent Domain | 6 |
| Conversation Domain | 7 |
| Decision Domain | 8 |
| Execution Domain | 7 |
| Governance Domain | 9 |
| Observability Domain | 5 |

## Contract and Event Matrix

| Capability | Contract | Event | Produced References | Authority |
|---|---|---|---|---|
| `CAP-IDN-001` CreateOrganization | `CON-IDN-001` CreateOrganizationCommand | `EVT-IDN-001` OrganizationCreated | OrganizationReference | Governance Authority |
| `CAP-IDN-002` ActivateOrganization | `CON-IDN-002` ActivateOrganizationCommand | `EVT-IDN-002` OrganizationActivated | OrganizationReference | Governance Authority |
| `CAP-IDN-003` SuspendOrganization | `CON-IDN-003` SuspendOrganizationCommand | `EVT-IDN-003` OrganizationSuspended | OrganizationReference | Governance Authority |
| `CAP-IDN-004` ArchiveOrganization | `CON-IDN-004` ArchiveOrganizationCommand | `EVT-IDN-004` OrganizationArchived | OrganizationReference | Governance Authority |
| `CAP-IDN-005` CreateWorkspace | `CON-IDN-005` CreateWorkspaceCommand | `EVT-IDN-005` WorkspaceCreated | WorkspaceReference | Governance Authority |
| `CAP-IDN-006` InviteMember | `CON-IDN-006` InviteMemberCommand | `EVT-IDN-006` MemberInvited | OrganizationReference | Governance Authority |
| `CAP-IDN-007` ActivateMembership | `CON-IDN-007` ActivateMembershipCommand | `EVT-IDN-007` MembershipActivated | OrganizationReference | Governance Authority |
| `CAP-IDN-008` SuspendMembership | `CON-IDN-008` SuspendMembershipCommand | `EVT-IDN-008` MembershipSuspended | OrganizationReference | Governance Authority |
| `CAP-IDN-009` RevokeMembership | `CON-IDN-009` RevokeMembershipCommand | `EVT-IDN-009` MembershipRevoked | OrganizationReference | Governance Authority |
| `CAP-KNW-001` CreateKnowledgeAsset | `CON-KNW-001` CreateKnowledgeAssetCommand | `EVT-KNW-001` KnowledgeAssetCreated | KnowledgeAssetReference | Knowledge Authority |
| `CAP-KNW-002` ValidateKnowledgeAsset | `CON-KNW-002` ValidateKnowledgeAssetCommand | `EVT-KNW-002` KnowledgeAssetValidated | KnowledgeAssetReference | Knowledge Authority |
| `CAP-KNW-003` ApproveKnowledgeAsset | `CON-KNW-003` ApproveKnowledgeAssetCommand | `EVT-KNW-003` KnowledgeAssetApproved | KnowledgeAssetReference | Knowledge Authority |
| `CAP-KNW-004` OperationalizeKnowledgeAsset | `CON-KNW-004` OperationalizeKnowledgeAssetCommand | `EVT-KNW-004` KnowledgeAssetOperationalized | KnowledgeAssetReference | Knowledge Authority |
| `CAP-KNW-005` ArchiveKnowledgeAsset | `CON-KNW-005` ArchiveKnowledgeAssetCommand | `EVT-KNW-005` KnowledgeAssetArchived | KnowledgeAssetReference | Knowledge Authority |
| `CAP-AGT-001` CreateAgent | `CON-AGT-001` CreateAgentCommand | `EVT-AGT-001` AgentCreated | AgentReference | Capability Authority |
| `CAP-AGT-002` ApproveAgent | `CON-AGT-002` ApproveAgentCommand | `EVT-AGT-002` AgentApproved | AgentReference | Capability Authority |
| `CAP-AGT-003` BindCapability | `CON-AGT-003` BindCapabilityCommand | `EVT-AGT-003` CapabilityBound | AgentReference | Capability Authority |
| `CAP-AGT-004` ActivateAgent | `CON-AGT-004` ActivateAgentCommand | `EVT-AGT-004` AgentActivated | AgentReference | Capability Authority |
| `CAP-AGT-005` SuspendAgent | `CON-AGT-005` SuspendAgentCommand | `EVT-AGT-005` AgentSuspended | AgentReference | Capability Authority |
| `CAP-AGT-006` ArchiveAgent | `CON-AGT-006` ArchiveAgentCommand | `EVT-AGT-006` AgentArchived | AgentReference | Capability Authority |
| `CAP-CON-001` OpenConversation | `CON-CON-001` OpenConversationCommand | `EVT-CON-001` ConversationCreated | ConversationReference | Runtime Authority |
| `CAP-CON-002` AppendMessage | `CON-CON-002` AppendMessageCommand | `EVT-CON-002` MessageRecorded | ConversationReference | Runtime Authority |
| `CAP-CON-003` ResolveContext | `CON-CON-003` ResolveContextCommand | `EVT-CON-003` ContextResolved | ConversationReference | Runtime Authority |
| `CAP-CON-004` PauseConversation | `CON-CON-004` PauseConversationCommand | `EVT-CON-004` ConversationPaused | ConversationReference | Runtime Authority |
| `CAP-CON-005` ResumeConversation | `CON-CON-005` ResumeConversationCommand | `EVT-CON-005` ConversationResumed | ConversationReference | Runtime Authority |
| `CAP-CON-006` CloseConversation | `CON-CON-006` CloseConversationCommand | `EVT-CON-006` ConversationClosed | ConversationReference | Runtime Authority |
| `CAP-CON-007` ArchiveConversation | `CON-CON-007` ArchiveConversationCommand | `EVT-CON-007` ConversationArchived | ConversationReference | Runtime Authority |
| `CAP-DEC-001` CreateDecision | `CON-DEC-001` CreateDecisionCommand | `EVT-DEC-001` DecisionCreated | DecisionReference | Decision Authority |
| `CAP-DEC-002` AttachEvidence | `CON-DEC-002` AttachEvidenceCommand | `EVT-DEC-002` EvidenceAttached | EvidenceReference | Decision Authority |
| `CAP-DEC-003` SubmitDecisionReview | `CON-DEC-003` SubmitDecisionReviewCommand | `EVT-DEC-003` DecisionSubmitted | DecisionReference | Decision Authority |
| `CAP-DEC-004` ApproveDecision | `CON-DEC-004` ApproveDecisionCommand | `EVT-DEC-004` DecisionApproved | DecisionReference | Decision Authority |
| `CAP-DEC-005` RejectDecision | `CON-DEC-005` RejectDecisionCommand | `EVT-DEC-005` DecisionRejected | DecisionReference | Decision Authority |
| `CAP-DEC-006` PublishDecision | `CON-DEC-006` PublishDecisionCommand | `EVT-DEC-006` DecisionPublished | DecisionReference | Decision Authority |
| `CAP-DEC-007` SupersedeDecision | `CON-DEC-007` SupersedeDecisionCommand | `EVT-DEC-007` DecisionSuperseded | DecisionReference | Decision Authority |
| `CAP-DEC-008` ArchiveDecision | `CON-DEC-008` ArchiveDecisionCommand | `EVT-DEC-008` DecisionArchived | DecisionReference | Decision Authority |
| `CAP-EXE-001` PlanExecution | `CON-EXE-001` PlanExecutionCommand | `EVT-EXE-001` ExecutionPlanned | ExecutionReference | Runtime Authority |
| `CAP-EXE-002` AuthorizeExecution | `CON-EXE-002` AuthorizeExecutionCommand | `EVT-EXE-002` ExecutionAuthorized | ExecutionReference | Runtime Authority |
| `CAP-EXE-003` StartExecution | `CON-EXE-003` StartExecutionCommand | `EVT-EXE-003` ExecutionStarted | ExecutionReference | Runtime Authority |
| `CAP-EXE-004` CompleteExecution | `CON-EXE-004` CompleteExecutionCommand | `EVT-EXE-004` ExecutionCompleted | ExecutionReference | Runtime Authority |
| `CAP-EXE-005` VerifyExecution | `CON-EXE-005` VerifyExecutionCommand | `EVT-EXE-005` ExecutionVerified | ExecutionReference | Runtime Authority |
| `CAP-EXE-006` ArchiveExecution | `CON-EXE-006` ArchiveExecutionCommand | `EVT-EXE-006` ExecutionArchived | ExecutionReference | Runtime Authority |
| `CAP-EXE-007` PromoteArtifactToKnowledge | `CON-EXE-007` PromoteArtifactToKnowledgeCommand | `EVT-EXE-007` ExecutionArtifactProduced | KnowledgeAssetReference | Runtime Authority |
| `CAP-GOV-001` CreatePolicy | `CON-GOV-001` CreatePolicyCommand | `EVT-GOV-001` PolicyCreated | PolicyReference | Governance Authority |
| `CAP-GOV-002` SubmitPolicyReview | `CON-GOV-002` SubmitPolicyReviewCommand | `EVT-GOV-002` PolicySubmitted | PolicyReference | Governance Authority |
| `CAP-GOV-003` ApprovePolicy | `CON-GOV-003` ApprovePolicyCommand | `EVT-GOV-003` PolicyApproved | PolicyReference | Governance Authority |
| `CAP-GOV-004` RejectPolicy | `CON-GOV-004` RejectPolicyCommand | `EVT-GOV-004` PolicyRejected | PolicyReference | Governance Authority |
| `CAP-GOV-005` PublishPolicy | `CON-GOV-005` PublishPolicyCommand | `EVT-GOV-005` PolicyPublished | PolicyReference | Governance Authority |
| `CAP-GOV-006` SupersedePolicy | `CON-GOV-006` SupersedePolicyCommand | `EVT-GOV-006` PolicySuperseded | PolicyReference | Governance Authority |
| `CAP-GOV-007` DelegateAuthority | `CON-GOV-007` DelegateAuthorityCommand | `EVT-GOV-007` DelegationGranted | PolicyReference | Governance Authority |
| `CAP-GOV-008` RevokeDelegation | `CON-GOV-008` RevokeDelegationCommand | `EVT-GOV-008` DelegationRevoked | PolicyReference | Governance Authority |
| `CAP-GOV-009` ArchivePolicy | `CON-GOV-009` ArchivePolicyCommand | `EVT-GOV-009` PolicyArchived | PolicyReference | Governance Authority |
| `CAP-OBS-001` RegisterAuditRecord | `CON-OBS-001` RegisterAuditRecordCommand | `EVT-OBS-001` AuditRecordRegistered | AuditRecordReference | Observability Authority |
| `CAP-OBS-002` ValidateEvidence | `CON-OBS-002` ValidateEvidenceCommand | `EVT-OBS-002` EvidenceValidated | AuditRecordReference | Observability Authority |
| `CAP-OBS-003` CorrelateEvidence | `CON-OBS-003` CorrelateEvidenceCommand | `EVT-OBS-003` EvidenceCorrelated | AuditRecordReference | Observability Authority |
| `CAP-OBS-004` ApplyRetentionPolicy | `CON-OBS-004` ApplyRetentionPolicyCommand | `EVT-OBS-004` RetentionApplied | AuditRecordReference | Observability Authority |
| `CAP-OBS-005` ArchiveEvidence | `CON-OBS-005` ArchiveEvidenceCommand | `EVT-OBS-005` AuditRecordArchived | AuditRecordReference | Observability Authority |

## Validation Gates

Before promotion, OES-RC-0004-R1 MUST satisfy:

- 56/56 capabilities projected.
- 56 unique command contracts.
- 56 unique primary events.
- zero references outside the OES-006 vocabulary.
- zero forbidden non-canonical references.
- zero files outside `/specification`.
- zero runtime, API, database or infrastructure changes.
- manifest hashes verified.

## Risk Residual

OES-007 defines the contract/event surface but does not yet validate runtime behavior. Runtime implementation remains pending for a later OES stage and must not be inferred from this document.

## Promotion Recommendation

Promote only after independent READONLY_AUDIT confirms package integrity, manifest validity, coverage, vocabulary closure and collision safety against the target commit.
