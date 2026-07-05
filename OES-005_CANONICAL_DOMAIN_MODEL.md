# OES-005 — Canonical Domain Model

**Title:** Canonical Domain Model  
**Version:** 0.1-rc-r4  
**Status:** Release Candidate  
**Owner:** Chief Architecture & Engineering Officer (AO-01)  
**Approver:** Vision Owner + Independent Engineering Auditor  

## Dependencies

- OES-001 — Engineering Constitution (Baseline)
- OES-002 — Engineering Glossary (Baseline)
- OES-003 — Engineering Governance (Baseline)
- OES-004 — Engineering Delivery Standard (Baseline)

Baseline evidence is external to this package and is declared in `specification/packages/OES-RC-0002-R3/OES-RC-0002-R3_BASELINE_REFERENCE.md`.

## Objective

Define the canonical domain model of ORKIO as the single source of truth for domain concepts, aggregate roots, entities, value objects, domain services, references, authorities, invariants, relationships, capabilities, contracts, events, state transitions, ownership and traceability.

All downstream specifications shall derive from this document and shall not redefine domain concepts.

## Scope

Included:

- Identity Domain
- Knowledge Domain
- Agent Domain
- Conversation Domain
- Decision Domain
- Execution Domain
- Governance Domain
- Observability Domain
- Domain ownership rules
- Evidence taxonomy and ownership
- Capability derivation requirements
- State transition alignment
- Cross-aggregate reference rules

## Out of Scope

This document does not specify APIs, databases, runtime implementation, infrastructure, frameworks, cloud providers, AI providers, communication protocols or deployment.

## Domain Definition

The ORKIO domain is the set of canonical concepts, rules, responsibilities and relationships that define the operational reality of the ORKIO platform independently of implementation technology.

## Mission Alignment

Every domain element shall support the value chain:

`Knowledge → Analysis → Decision → Execution → Institutional Learning`

## Domain Principles

- **DP-001 — Domain First:** implementation shall not redefine domain concepts.
- **DP-002 — Single Authority:** each canonical concept shall have exactly one owning authority.
- **DP-003 — Institutional Knowledge:** knowledge belongs to the organization, never to an agent, model provider or runtime.
- **DP-004 — Governed Decisions:** the primary business artifact is the governed Decision.
- **DP-005 — Traceable Execution:** every relevant execution shall be identifiable, traceable and auditable.
- **DP-006 — Continuous Learning:** execution outcomes may produce institutional knowledge.
- **DP-007 — Technology Independence:** domain concepts are independent of implementation technology.
- **DP-008 — No Cross-Aggregate Mutation:** an aggregate may reference another aggregate but shall not mutate entities owned by another aggregate.
- **DP-009 — Lifecycle Metadata Mutability:** immutable domain content may still receive authorized lifecycle metadata transitions.
- **DP-010 — Reference Is Not Ownership:** cross-aggregate references never transfer ownership.
- **DP-011 — Canonical Reference Closure:** every named reference used by an aggregate shall appear exactly once in the Canonical Concept Inventory as type `Reference` with stable ID and owning authority.

## Meta-Model

| Type | Definition |
|---|---|
| Aggregate Root | Entity governing consistency boundaries for an aggregate. |
| Entity | Domain concept with identity and lifecycle owned by one aggregate. |
| Value Object | Immutable concept without independent identity. |
| Reference | Stable pointer to a concept owned by another aggregate; not an entity and not ownership. |
| Domain Service | Stateless behavior operating across concepts without owning identity. |
| Authority | Governance role responsible for a domain boundary. |
| Policy | Versioned governance rule set. |
| Capability | Authorized action derivable from the domain. |
| Contract | Interface intention derived from a capability. |
| Event | Immutable fact produced by a contract or transition. |

## Canonical Concept Inventory

### Aggregate Roots

| Domain ID | Concept | Type | Owning Authority |
|---|---|---|---|
| DOM-001 | Organization | Aggregate Root | Governance Authority |
| DOM-010 | KnowledgeAsset | Aggregate Root | Knowledge Authority |
| DOM-020 | Agent | Aggregate Root | Capability Authority |
| DOM-030 | Conversation | Aggregate Root | Runtime Authority |
| DOM-040 | Decision | Aggregate Root | Decision Authority |
| DOM-050 | Execution | Aggregate Root | Runtime Authority |
| DOM-060 | Policy | Aggregate Root | Governance Authority |
| DOM-070 | AuditRecord | Aggregate Root | Observability Authority |

### Entities

| Domain ID | Concept | Owning Authority |
|---|---|---|
| DOM-002 | Workspace | Governance Authority |
| DOM-003 | Person | Governance Authority |
| DOM-004 | Membership | Governance Authority |
| DOM-011 | KnowledgeSource | Knowledge Authority |
| DOM-012 | KnowledgeCollection | Knowledge Authority |
| DOM-013 | KnowledgeReference | Knowledge Authority |
| DOM-021 | AgentProfile | Capability Authority |
| DOM-022 | CapabilityBinding | Capability Authority |
| DOM-031 | Message | Runtime Authority |
| DOM-032 | Participant | Runtime Authority |
| DOM-033 | Attachment | Runtime Authority |
| DOM-041 | DecisionEvidence | Decision Authority |
| DOM-043 | Rationale | Decision Authority |
| DOM-044 | Approval | Decision Authority |
| DOM-045 | DecisionOutcome | Decision Authority |
| DOM-051 | Task | Runtime Authority |
| DOM-052 | Artifact | Runtime Authority |
| DOM-053 | ExecutionResult | Runtime Authority |
| DOM-054 | ExecutionEvidence | Runtime Authority |
| DOM-061 | Rule | Governance Authority |
| DOM-062 | Authority | Governance Authority |
| DOM-063 | Constraint | Governance Authority |
| DOM-064 | ApprovalPolicy | Governance Authority |
| DOM-065 | Delegation | Governance Authority |
| DOM-071 | AuditEvidence | Observability Authority |
| DOM-072 | AuditReference | Observability Authority |

### Value Objects

| Domain ID | Concept | Owning Authority |
|---|---|---|
| DOM-005 | Role | Governance Authority |
| DOM-014 | Classification | Knowledge Authority |
| DOM-015 | Provenance | Knowledge Authority |
| DOM-016 | KnowledgeVersion | Knowledge Authority |
| DOM-023 | AgentConfiguration | Capability Authority |
| DOM-024 | RuntimeContext | Runtime Authority |
| DOM-034 | ContextSnapshot | Runtime Authority |
| DOM-042 | EvidenceReference | Decision Authority |
| DOM-047 | DecisionVersion | Decision Authority |
| DOM-056 | ExecutionVersion | Runtime Authority |
| DOM-066 | PolicyVersion | Governance Authority |
| DOM-073 | AuditScope | Observability Authority |
| DOM-074 | Correlation | Observability Authority |
| DOM-075 | AuditVersion | Observability Authority |
| DOM-076 | RetentionClass | Observability Authority |

### References

References are stable value objects used to point to concepts owned by another aggregate. A reference does not transfer ownership, does not permit mutation of the target aggregate, and shall be resolved only through contracts owned by the target aggregate.

| Domain ID | Concept | Type | Target Aggregate | Owning Authority |
|---|---|---|---|---|
| DOM-080 | OrganizationReference | Reference | Organization | Governance Authority |
| DOM-081 | WorkspaceReference | Reference | Workspace | Governance Authority |
| DOM-082 | KnowledgeAssetReference | Reference | KnowledgeAsset | Knowledge Authority |
| DOM-083 | AgentReference | Reference | Agent | Capability Authority |
| DOM-084 | CapabilityReference | Reference | Capability | Capability Authority |
| DOM-085 | ConversationReference | Reference | Conversation | Runtime Authority |
| DOM-086 | DecisionReference | Reference | Decision | Decision Authority |
| DOM-087 | ExecutionReference | Reference | Execution | Runtime Authority |
| DOM-088 | PolicyReference | Reference | Policy | Governance Authority |
| DOM-089 | AuditRecordReference | Reference | AuditRecord | Observability Authority |

### Reserved Concepts

| Domain ID | Concept | Status | Rule |
|---|---|---|---|
| DOM-090 | Learning | Reserved | Domain outcome; not promoted to aggregate in this RC. |
| DOM-091 | KnowledgeArtifact | Reserved | Potential future representation of KnowledgeAsset. |
| DOM-092 | AgentPersona | Reserved | Potential future separation from AgentProfile. |

## Authority Definitions

| Authority | Responsibility |
|---|---|
| Governance Authority | Policies, authorities, delegations, institutional responsibility. |
| Knowledge Authority | Knowledge integrity, classification, provenance, versioning and retention. |
| Capability Authority | Agent profiles, capability bindings and operational enablement. |
| Decision Authority | Decision legitimacy, approval, rejection, publication and supersession. |
| Runtime Authority | Operational execution, conversation continuity and execution lifecycle. |
| Observability Authority | Audit evidence, evidence retention, correlation and audit retrieval. |

Named policies such as `Runtime Policy`, `Decision Policy`, `Retention Policy`, `Knowledge Policy` and `Capability Policy` are policy types or policy instances owned by Governance Authority unless explicitly delegated by an approved Policy. They are not separate authorities.

## Evidence Taxonomy and Ownership

Evidence is a semantic category with owned representations.

| Evidence Representation | Owner | Rule |
|---|---|---|
| DecisionEvidence | Decision Authority | Created and governed inside Decision. |
| ExecutionEvidence | Runtime Authority | Created and governed inside Execution. |
| AuditEvidence | Observability Authority | Registered and governed inside Observability. |
| EvidenceReference | Decision Authority | References admissible evidence owned by another aggregate without ownership transfer. |

Rules:

- Decision may reference ExecutionEvidence or AuditEvidence through EvidenceReference.
- Execution creates ExecutionEvidence, not generic Evidence.
- Observability records AuditEvidence or an immutable audit representation of evidence.
- No aggregate mutates evidence owned by another aggregate.

## Immutability and Lifecycle Rule

When an aggregate is declared immutable after approval or registration, the immutable scope applies to business content and evidential content.

Authorized lifecycle metadata may still transition according to the state machine when governed by the owning authority.

Examples:

- Decision content, rationale and approved evidence are immutable after approval; lifecycle metadata may transition Approved → Effective → Superseded → Archived.
- AuditRecord evidential payload is immutable after registration; lifecycle metadata may transition Registered → Validated → Retained → Archived.
- Policy content is immutable after becoming Effective; lifecycle metadata may transition Effective → Superseded → Archived.

## Aggregate Specifications

### Identity Domain

**Aggregate Root:** DOM-001 Organization  
**Authority:** Governance Authority  
**Objective:** Establish identity, membership and organizational responsibility.

**Entities:** Workspace, Person, Membership.  
**Value Objects:** Role.  
**References:** none.  
**Lifecycle:** Organization has `Draft → Active → Suspended → Archived`. Membership has `Pending → Active → Suspended → Revoked`.

**Invariants:**

- INV-IDN-001: Organization has unique identity.
- INV-IDN-002: Organization has exactly one Governance Authority.
- INV-IDN-003: Workspace belongs to exactly one Organization.
- INV-IDN-004: Person participates in Organization only through Membership.
- INV-IDN-005: Role classifies responsibility; Policy governs permission.
- INV-IDN-006: Organization lifecycle transitions require Governance Authority.

**Expected Capabilities:**

| ID | Capability | Purpose | Inputs | Outputs | Policy/Auth | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|
| CAP-IDN-001 | CreateOrganization | Create organization boundary. | Organization profile | Organization Draft | Governance Policy | none | Organization exists with unique ID. |
| CAP-IDN-002 | ActivateOrganization | Activate organization. | Organization Draft | Organization Active | Governance Authority | Organization | Organization is active and auditable. |
| CAP-IDN-003 | SuspendOrganization | Suspend organization. | Organization Active | Organization Suspended | Governance Authority | Organization | Organization is suspended with rationale. |
| CAP-IDN-004 | ArchiveOrganization | Archive organization. | Organization terminal | Organization Archived | Retention Policy | Organization | Organization remains retrievable by policy. |
| CAP-IDN-005 | CreateWorkspace | Create operational workspace. | Organization, workspace profile | Workspace | Governance Policy | Organization Active | Workspace belongs to one Organization. |
| CAP-IDN-006 | InviteMember | Initiate membership. | Person, Organization/Workspace | Membership Pending | Governance Policy | Person, Organization | Membership is pending and auditable. |
| CAP-IDN-007 | ActivateMembership | Activate membership. | Membership Pending | Membership Active | Governance Policy | Membership | Membership is active under valid policy. |
| CAP-IDN-008 | SuspendMembership | Suspend membership. | Membership Active | Membership Suspended | Governance Policy | Membership | Membership is suspended with rationale. |
| CAP-IDN-009 | RevokeMembership | Revoke membership. | Membership Active/Suspended | Membership Revoked | Governance Policy | Membership | Membership no longer grants participation. |

**Expected Contracts:** CreateOrganization, ActivateOrganization, SuspendOrganization, ArchiveOrganization, CreateWorkspace, InviteMember, ActivateMembership, SuspendMembership, RevokeMembership.  
**Expected Events:** OrganizationCreated, OrganizationActivated, OrganizationSuspended, OrganizationArchived, WorkspaceCreated, MemberInvited, MembershipActivated, MembershipSuspended, MembershipRevoked.

### Knowledge Domain

**Aggregate Root:** DOM-010 KnowledgeAsset  
**Authority:** Knowledge Authority  
**Objective:** Preserve institutional knowledge as a governed asset.

**Entities:** KnowledgeSource, KnowledgeCollection, KnowledgeReference.  
**Value Objects:** Classification, Provenance, KnowledgeVersion.  
**References:** none.  
**Lifecycle:** `Draft → Validated → Approved → Operational → Archived`.

**Invariants:**

- INV-KNW-001: KnowledgeAsset has unique identity.
- INV-KNW-002: KnowledgeAsset has at least one KnowledgeSource.
- INV-KNW-003: KnowledgeAsset has exactly one Knowledge Authority.
- INV-KNW-004: Every modification creates a new KnowledgeVersion.
- INV-KNW-005: Provenance is preserved across versions.
- INV-KNW-006: Knowledge belongs to Organization, never to agent, model or runtime.

**Expected Capabilities:**

| ID | Capability | Purpose | Inputs | Outputs | Policy/Auth | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|
| CAP-KNW-001 | CreateKnowledgeAsset | Register institutional knowledge. | Source, classification, content reference | KnowledgeAsset Draft | Knowledge Policy | Organization | Asset has ID, source and classification. |
| CAP-KNW-002 | ValidateKnowledgeAsset | Validate knowledge quality. | KnowledgeAsset Draft | KnowledgeAsset Validated | Knowledge Authority | KnowledgeAsset | Validation evidence is recorded. |
| CAP-KNW-003 | ApproveKnowledgeAsset | Approve institutional use. | KnowledgeAsset Validated | KnowledgeAsset Approved | Knowledge Authority | Validation | Approval is auditable. |
| CAP-KNW-004 | OperationalizeKnowledgeAsset | Make asset operational. | KnowledgeAsset Approved | KnowledgeAsset Operational | Knowledge Policy | Approved Asset | Asset is available for authorized use. |
| CAP-KNW-005 | ArchiveKnowledgeAsset | Archive asset. | KnowledgeAsset | KnowledgeAsset Archived | Retention Policy | KnowledgeAsset | Archived asset retains provenance. |

**Expected Contracts:** CreateKnowledgeAsset, ValidateKnowledgeAsset, ApproveKnowledgeAsset, OperationalizeKnowledgeAsset, ArchiveKnowledgeAsset.  
**Expected Events:** KnowledgeAssetCreated, KnowledgeAssetValidated, KnowledgeAssetApproved, KnowledgeAssetOperationalized, KnowledgeAssetArchived.

### Agent Domain

**Aggregate Root:** DOM-020 Agent  
**Authority:** Capability Authority  
**Objective:** Govern operational agents as capability executors.

**Entities:** AgentProfile, CapabilityBinding.  
**Value Objects:** AgentConfiguration, RuntimeContext.  
**References:** AuditRecordReference through Observability correlation only.  
**Lifecycle:** `Draft → Approved → Active → Suspended → Archived`.

**Invariants:**

- INV-AGT-001: Agent has unique identity.
- INV-AGT-002: Agent executes only authorized capabilities.
- INV-AGT-003: Agent has no domain authority by itself.
- INV-AGT-004: Every execution occurs under policy.
- INV-AGT-005: RuntimeContext is transient and does not mutate Agent state.
- INV-AGT-006: Execution history is observed through AuditRecord references and is not owned by Agent.

**Expected Capabilities:**

| ID | Capability | Purpose | Inputs | Outputs | Policy/Auth | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|
| CAP-AGT-001 | CreateAgent | Create agent profile. | AgentProfile | Agent Draft | Capability Policy | Workspace | Agent has identity and profile. |
| CAP-AGT-002 | ApproveAgent | Approve agent use. | Agent Draft | Agent Approved | Capability Authority | Agent | Approval recorded. |
| CAP-AGT-003 | BindCapability | Bind authorized capability. | Agent, Capability | CapabilityBinding | Capability Policy | Agent, Capability | Agent can execute bound capability only. |
| CAP-AGT-004 | ActivateAgent | Activate agent. | Agent Approved | Agent Active | Capability Authority | Approved Agent | Agent active under policy. |
| CAP-AGT-005 | SuspendAgent | Suspend agent. | Agent Active | Agent Suspended | Capability Authority | Agent | Agent cannot execute capabilities. |
| CAP-AGT-006 | ArchiveAgent | Archive agent. | Agent Suspended/Approved | Agent Archived | Retention Policy | Agent | Agent remains auditable and inactive. |

**Expected Contracts:** CreateAgent, ApproveAgent, BindCapability, ActivateAgent, SuspendAgent, ArchiveAgent.  
**Expected Events:** AgentCreated, AgentApproved, CapabilityBound, AgentActivated, AgentSuspended, AgentArchived.

### Conversation Domain

**Aggregate Root:** DOM-030 Conversation  
**Authority:** Runtime Authority  
**Objective:** Preserve contextual continuity for interactions.

**Entities:** Message, Participant, Attachment.  
**Value Objects:** ContextSnapshot.  
**References:** KnowledgeAssetReference, DecisionReference, ExecutionReference when applicable.  
**Lifecycle:** `Created → Active → Paused → Active → Closed → Archived`.

**Invariants:**

- INV-CON-001: Conversation belongs to exactly one Workspace.
- INV-CON-002: Message belongs to exactly one Conversation.
- INV-CON-003: Conversation has at least one Participant.
- INV-CON-004: Conversation references KnowledgeAsset but does not own it.
- INV-CON-005: Decision derived from Conversation preserves traceability.

**Expected Capabilities:**

| ID | Capability | Purpose | Inputs | Outputs | Policy/Auth | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|
| CAP-CON-001 | OpenConversation | Start contextual interaction. | Workspace, participant | Conversation Created | Runtime Policy | Workspace | Conversation has ID and participant. |
| CAP-CON-002 | AppendMessage | Record message. | Conversation, message | Message / Conversation Active | Runtime Policy | Conversation | Message belongs to one Conversation. |
| CAP-CON-003 | ResolveContext | Resolve active context. | Conversation | ContextSnapshot | Runtime Policy | Conversation, Knowledge refs | Context is consistent and authorized. |
| CAP-CON-004 | PauseConversation | Pause interaction. | Conversation Active | Conversation Paused | Runtime Policy | Conversation | Conversation cannot accept normal messages. |
| CAP-CON-005 | ResumeConversation | Resume interaction. | Conversation Paused | Conversation Active | Runtime Policy | Conversation | Conversation is active again. |
| CAP-CON-006 | CloseConversation | Close interaction. | Conversation Active/Paused | Conversation Closed | Runtime Policy | Conversation | Conversation cannot accept normal messages. |
| CAP-CON-007 | ArchiveConversation | Archive context. | Conversation Closed | Conversation Archived | Retention Policy | Conversation | Context remains retrievable by policy. |

**Expected Contracts:** OpenConversation, AppendMessage, ResolveContext, PauseConversation, ResumeConversation, CloseConversation, ArchiveConversation.  
**Expected Events:** ConversationCreated, MessageRecorded, ContextResolved, ConversationPaused, ConversationResumed, ConversationClosed, ConversationArchived.

### Decision Domain

**Aggregate Root:** DOM-040 Decision  
**Authority:** Decision Authority  
**Objective:** Govern institutional decisions as primary business artifacts.

**Entities:** DecisionEvidence, Rationale, Approval, DecisionOutcome.  
**Value Objects:** EvidenceReference, DecisionVersion.  
**References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference.  
**Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`.

**Rejected Rule:** A rejected Decision is terminal for that version. Rework creates a new DecisionVersion or a new Draft Decision referencing the rejected one.

**Invariants:**

- INV-DEC-001: Decision has unique identity.
- INV-DEC-002: Decision references at least one admissible EvidenceReference before approval.
- INV-DEC-003: Decision has exactly one Decision Authority.
- INV-DEC-004: Approved Decision business content is immutable; lifecycle metadata may transition by authorized contract.
- INV-DEC-005: Decision preserves Rationale.
- INV-DEC-006: Decision references production context.
- INV-DEC-007: Decision is fully auditable.
- INV-DEC-008: Decision does not depend on an AI provider.

**Expected Capabilities:**

| ID | Capability | Purpose | Inputs | Outputs | Policy/Auth | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|
| CAP-DEC-001 | CreateDecision | Create draft decision. | Context, rationale draft | Decision Draft | Decision Policy | Conversation/Knowledge | Draft has ID and context. |
| CAP-DEC-002 | AttachEvidence | Attach admissible evidence reference. | Decision, EvidenceReference | Decision with Evidence | Decision Policy | Evidence owner | EvidenceReference is valid and owned. |
| CAP-DEC-003 | SubmitDecisionReview | Submit for review. | Decision Draft | Decision Under Review | Decision Policy | Evidence, Rationale | Decision has minimum evidence and rationale. |
| CAP-DEC-004 | ApproveDecision | Approve decision. | Decision Under Review | Decision Approved | Decision Authority | Review | Approval is recorded; content immutable. |
| CAP-DEC-005 | RejectDecision | Reject decision. | Decision Under Review | Decision Rejected | Decision Authority | Review | Rejection rationale is recorded. |
| CAP-DEC-006 | PublishDecision | Make effective. | Decision Approved | Decision Effective | Decision Policy | Approval | EffectiveDate is recorded. |
| CAP-DEC-007 | SupersedeDecision | Replace decision. | Decision Effective, new Decision | Decision Superseded | Decision Authority | New Decision | Supersession reference is recorded. |
| CAP-DEC-008 | ArchiveDecision | Archive decision. | Decision terminal | Decision Archived | Retention Policy | Decision | Decision remains auditable. |

**Expected Contracts:** CreateDecision, AttachEvidence, SubmitDecisionReview, ApproveDecision, RejectDecision, PublishDecision, SupersedeDecision, ArchiveDecision.  
**Expected Events:** DecisionCreated, EvidenceAttached, DecisionSubmitted, DecisionApproved, DecisionRejected, DecisionPublished, DecisionSuperseded, DecisionArchived.

### Execution Domain

**Aggregate Root:** DOM-050 Execution  
**Authority:** Runtime Authority  
**Objective:** Materialize decisions or policies into governed action.

**Entities:** Task, Artifact, ExecutionResult, ExecutionEvidence.  
**Value Objects:** ExecutionVersion.  
**References:** DecisionReference, PolicyReference, KnowledgeAssetReference, AuditRecordReference.  
**Lifecycle:** `Planned → Authorized → Running → Completed → Verified → Archived`.

**Invariants:**

- INV-EXE-001: Execution references exactly one Decision or Policy authorizer.
- INV-EXE-002: Execution has unique identity.
- INV-EXE-003: Completed or Verified Execution produces at least one ExecutionEvidence.
- INV-EXE-004: Execution has known state.
- INV-EXE-005: ExecutionResult never replaces Decision.
- INV-EXE-006: Execution may produce new KnowledgeAssets through Knowledge Authority.
- INV-EXE-007: Execution preserves full traceability.

**Expected Capabilities:**

| ID | Capability | Purpose | Inputs | Outputs | Policy/Auth | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|
| CAP-EXE-001 | PlanExecution | Plan execution from authorizer. | Decision/Policy | Execution Planned | Runtime Policy | Decision/Policy | Plan references authorizer. |
| CAP-EXE-002 | AuthorizeExecution | Authorize execution. | Execution Planned | Execution Authorized | Runtime Authority | Plan | Authorization recorded. |
| CAP-EXE-003 | StartExecution | Start execution. | Execution Authorized | Execution Running | Runtime Policy | Authorization | Running state recorded. |
| CAP-EXE-004 | CompleteExecution | Complete execution. | Execution Running | Execution Completed | Runtime Policy | Tasks | Result and ExecutionEvidence recorded. |
| CAP-EXE-005 | VerifyExecution | Verify result. | Execution Completed | Execution Verified | Runtime Authority | Result, Evidence | ExecutionEvidence exists. |
| CAP-EXE-006 | ArchiveExecution | Archive execution. | Execution Verified | Execution Archived | Retention Policy | Execution | Audit trail preserved. |
| CAP-EXE-007 | PromoteArtifactToKnowledge | Request artifact promotion. | Artifact, provenance | KnowledgeAsset Draft | Knowledge Authority | Execution Artifact | Promotion creates KnowledgeAsset via Knowledge capability. |

**Expected Contracts:** PlanExecution, AuthorizeExecution, StartExecution, CompleteExecution, VerifyExecution, ArchiveExecution, PromoteArtifactToKnowledge.  
**Expected Events:** ExecutionPlanned, ExecutionAuthorized, ExecutionStarted, ExecutionCompleted, ExecutionVerified, ExecutionArchived, ExecutionArtifactProduced, ArtifactPromotionRequested, KnowledgeAssetCreated.

### Governance Domain

**Aggregate Root:** DOM-060 Policy  
**Authority:** Governance Authority  
**Objective:** Govern institutional rules, authorities, constraints and delegations.

**Entities:** Rule, Authority, Constraint, ApprovalPolicy, Delegation.  
**Value Objects:** PolicyVersion.  
**References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference.  
**Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`.

**Invariants:**

- INV-GOV-001: Policy has unique identity.
- INV-GOV-002: Policy has exactly one Governance Authority.
- INV-GOV-003: Rule belongs to exactly one Policy.
- INV-GOV-004: Delegation has explicit validity period.
- INV-GOV-005: Authority is never implicit.
- INV-GOV-006: Effective Policy business content is immutable; lifecycle metadata may transition by authorized contract.
- INV-GOV-007: Governance decisions are auditable.

**Expected Capabilities:**

| ID | Capability | Purpose | Inputs | Outputs | Policy/Auth | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|
| CAP-GOV-001 | CreatePolicy | Create draft policy. | Scope, rules draft | Policy Draft | Governance Policy | Organization | Policy has ID and scope. |
| CAP-GOV-002 | SubmitPolicyReview | Submit policy for review. | Policy Draft | Policy Under Review | Governance Policy | Policy | Review state recorded. |
| CAP-GOV-003 | ApprovePolicy | Approve policy. | Policy Under Review | Policy Approved | Governance Authority | Review | Approval recorded. |
| CAP-GOV-004 | RejectPolicy | Reject policy. | Policy Under Review | Policy Rejected | Governance Authority | Review | Rejection rationale recorded. |
| CAP-GOV-005 | PublishPolicy | Make policy effective. | Policy Approved | Policy Effective | Governance Authority | Approval | Effective period recorded. |
| CAP-GOV-006 | SupersedePolicy | Supersede effective policy. | Policy Effective, new Policy | Policy Superseded | Governance Authority | New Policy | Supersession reference recorded. |
| CAP-GOV-007 | DelegateAuthority | Grant delegation. | Authority, delegate, scope | Delegation | Governance Authority | Policy | Delegation has explicit validity. |
| CAP-GOV-008 | RevokeDelegation | Revoke delegation. | Delegation | Delegation Revoked | Governance Authority | Delegation | Revocation recorded. |
| CAP-GOV-009 | ArchivePolicy | Archive policy. | Policy terminal | Policy Archived | Retention Policy | Policy | Policy remains auditable. |

**Expected Contracts:** CreatePolicy, SubmitPolicyReview, ApprovePolicy, RejectPolicy, PublishPolicy, SupersedePolicy, DelegateAuthority, RevokeDelegation, ArchivePolicy.  
**Expected Events:** PolicyCreated, PolicySubmitted, PolicyApproved, PolicyRejected, PolicyPublished, PolicySuperseded, DelegationGranted, DelegationRevoked, PolicyArchived.

### Observability Domain

**Aggregate Root:** DOM-070 AuditRecord  
**Authority:** Observability Authority  
**Objective:** Preserve domain evidence for auditability and institutional learning.

**Entities:** AuditEvidence, AuditReference.  
**Value Objects:** AuditScope, Correlation, AuditVersion, RetentionClass.  
**References:** DecisionReference, ExecutionReference, KnowledgeAssetReference, PolicyReference.  
**Lifecycle:** `Registered → Validated → Retained → Archived`.

**Invariants:**

- INV-OBS-001: AuditRecord has unique identity.
- INV-OBS-002: AuditRecord evidential payload is immutable after registration; lifecycle metadata may transition by authorized contract.
- INV-OBS-003: Relevant Decision produces at least one AuditRecord.
- INV-OBS-004: Relevant Execution produces at least one AuditRecord.
- INV-OBS-005: AuditRecord has identifiable context.
- INV-OBS-006: Evidence has retention class.
- INV-OBS-007: Evidence can be correlated with origin context.

**Expected Capabilities:**

| ID | Capability | Purpose | Inputs | Outputs | Policy/Auth | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|
| CAP-OBS-001 | RegisterAuditRecord | Register evidence. | Context, evidence | AuditRecord Registered | Observability Policy | Origin aggregate | Record payload is immutable and correlated. |
| CAP-OBS-002 | ValidateEvidence | Validate evidence. | AuditRecord | AuditRecord Validated | Observability Authority | AuditRecord | Validation metadata recorded. |
| CAP-OBS-003 | CorrelateEvidence | Correlate records. | AuditRecords | Correlation | Observability Policy | Records | Correlation references origins. |
| CAP-OBS-004 | ApplyRetentionPolicy | Apply retention. | AuditRecord | AuditRecord Retained | Retention Policy | Policy | Retention class applied. |
| CAP-OBS-005 | ArchiveEvidence | Archive audit evidence. | AuditRecord Retained | AuditRecord Archived | Retention Policy | AuditRecord | Evidence remains retrievable by policy. |

**Expected Contracts:** RegisterAuditRecord, ValidateEvidence, CorrelateEvidence, ApplyRetentionPolicy, ArchiveEvidence.  
**Expected Events:** AuditRecordRegistered, EvidenceValidated, EvidenceCorrelated, RetentionApplied, AuditRecordArchived.

## Artifact Promotion Rule

An Execution Artifact is not automatically a KnowledgeAsset.

Promotion from Artifact to KnowledgeAsset requires the `PromoteArtifactToKnowledge` capability, which must result in a Knowledge Authority governed `CreateKnowledgeAsset` operation and the `KnowledgeAssetCreated` event.

## Cross-Aggregate Reference Rules

- References are Value Objects unless explicitly promoted by a future baseline.
- References preserve identity, source aggregate, target aggregate, target ID and optional version.
- References do not grant mutation rights.
- References do not transfer authority.
- Cross-context changes require a capability owned by the destination authority.

## State Machine Coverage Rule

Every lifecycle state declared in this document shall be reachable by at least one capability, contract and event, or be explicitly declared terminal.

## Acceptance Criteria

OES-005 is acceptable when:

- every aggregate root has a unique Domain ID;
- entities, value objects and references are separated;
- every authority is unique;
- every invariant has stable ID;
- every lifecycle transition has capability, contract and event coverage;
- downstream OES-006 through OES-010 can be derived without inventing new domain concepts;
- the model remains technology-independent;
- package metadata references the required foundation baseline gate without declaring unverifiable data.

## Risks

- Promoting the package before foundation baseline evidence is externally recorded.
- Treating references as ownership.
- Confusing immutable business content with authorized lifecycle metadata.
- Inventing downstream behavior outside the domain derivation chain.

## Next Steps

- Reaudit OES-RC-0002-R3.
- If GO, promote OES-005 to baseline only after OES-RC-0001-R3 application evidence is recorded.
- Start OES-006 only after baseline approval.

## Revision History

| Version | Date | Description |
|---|---|---|
| 0.1-rc | 2026-07-05 | Initial Canonical Domain Model release candidate. |
| 0.1-rc-r1 | 2026-07-05 | Added evidence ownership, metadata alignment, capability semantics and premium matrices. |
| 0.1-rc-r4 | 2026-07-05 | Fixed baseline gate, metamodel classification, lifecycle coverage, immutability semantics and executable collision preflight. |
