# OES-006 — Capability Catalog

**Title:** Capability Catalog
**Version:** 0.1-rc-r3
**Status:** Release Candidate
**Owner:** Chief Architecture & Engineering Officer (AO-01)
**Approver:** Vision Owner + Independent Engineering Auditor

## Dependencies

- OES-001 — Engineering Constitution (Baseline)
- OES-002 — Engineering Glossary (Baseline)
- OES-003 — Engineering Governance (Baseline)
- OES-004 — Engineering Delivery Standard (Baseline)
- OES-005 — Canonical Domain Model (Baseline / OES-RC-0002-R4)
- OES-RC-0002-R4 SHA-256: `4273278F9786F1E9F0EE86CB4F5D8577B47BA76C44866C16676C85738A66A20A`

## Objective

Define the normative Capability Catalog for ORKIO as a deterministic behavioral projection of OES-005. OES-006 specifies what the approved domain is capable of doing without introducing, renaming, removing or reinterpreting domain concepts.

## Scope

Includes the 56 capabilities canonically declared in OES-005, enriched with behavioral metadata required for derivation of contracts, events and runtime projections.

## Out of Scope

- APIs, endpoints and protocol definitions.
- Database schemas.
- Frontend behavior.
- Infrastructure and deployment.
- AI provider or model-specific behavior.
- New domain concepts not present in OES-005.

## Derivation Policy

The following fields are inherited from OES-005 and are immutable in OES-006:

- Capability ID
- Capability Name
- Aggregate Root
- Authority
- Lifecycle
- Applicable Aggregate Invariants
- Canonical References

The following fields are behavioral projections introduced by OES-006:

- Purpose
- Business Meaning
- Required Inputs
- Optional Inputs
- Produced Objects
- Produced References
- Preconditions
- Postconditions
- Failure Conditions
- Primary Contract
- Primary Event
- Runtime Projection
- Traceability
- Verification Status

## Capability Model

Each capability uses the same normative structure:

```text
Capability ID
Capability Name
Aggregate Root
Authority
Lifecycle
Category
Purpose
Business Meaning
Required Inputs
Optional Inputs
Produced Objects
Produced References
Preconditions
Postconditions
Failure Conditions
Primary Contract
Primary Event
Runtime Projection
Traceability
Derived From
Verification Status
```

## Capability Catalog

### Identity Domain
#### CAP-IDN-001 — CreateOrganization

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-001
- **Capability Name:** CreateOrganization
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Create organization boundary.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CreateOrganization` for `Organization`.
- **Required Inputs:** Organization profile
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Organization Draft
- **Produced References:** OrganizationReference
- **Preconditions:** Applicable policy/authority `Governance Policy` must be resolved.
- **Postconditions:** Organization exists with unique ID.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-001 — CreateOrganizationCommand
- **Primary Event:** EVT-IDN-001 — OrganizationCreated
- **Runtime Projection:** RUN-IDN-001 CreateOrganizationRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-001
- **Verification Status:** VERIFIED
#### CAP-IDN-002 — ActivateOrganization

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-002
- **Capability Name:** ActivateOrganization
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Activate organization.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ActivateOrganization` for `Organization`.
- **Required Inputs:** Organization Draft
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Organization Active
- **Produced References:** OrganizationReference
- **Preconditions:** `Organization` must be available and the applicable policy/authority `Governance Authority` must be resolved.
- **Postconditions:** Organization is active and auditable.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-002 — ActivateOrganizationCommand
- **Primary Event:** EVT-IDN-002 — OrganizationActivated
- **Runtime Projection:** RUN-IDN-002 ActivateOrganizationRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-002
- **Verification Status:** VERIFIED
#### CAP-IDN-003 — SuspendOrganization

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-003
- **Capability Name:** SuspendOrganization
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Suspend organization.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `SuspendOrganization` for `Organization`.
- **Required Inputs:** Organization Active
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Organization Suspended
- **Produced References:** OrganizationReference
- **Preconditions:** `Organization` must be available and the applicable policy/authority `Governance Authority` must be resolved.
- **Postconditions:** Organization is suspended with rationale.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-003 — SuspendOrganizationCommand
- **Primary Event:** EVT-IDN-003 — OrganizationSuspended
- **Runtime Projection:** RUN-IDN-003 SuspendOrganizationRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-003
- **Verification Status:** VERIFIED
#### CAP-IDN-004 — ArchiveOrganization

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-004
- **Capability Name:** ArchiveOrganization
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Archive organization.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ArchiveOrganization` for `Organization`.
- **Required Inputs:** Organization terminal
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Organization Archived
- **Produced References:** OrganizationReference
- **Preconditions:** `Organization` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Organization remains retrievable by policy.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-004 — ArchiveOrganizationCommand
- **Primary Event:** EVT-IDN-004 — OrganizationArchived
- **Runtime Projection:** RUN-IDN-004 ArchiveOrganizationRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-004
- **Verification Status:** VERIFIED
#### CAP-IDN-005 — CreateWorkspace

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-005
- **Capability Name:** CreateWorkspace
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Create operational workspace.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CreateWorkspace` for `Organization`.
- **Required Inputs:** Organization, workspace profile
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Workspace
- **Produced References:** WorkspaceReference
- **Preconditions:** `Organization Active` must be available and the applicable policy/authority `Governance Policy` must be resolved.
- **Postconditions:** Workspace belongs to one Organization.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-005 — CreateWorkspaceCommand
- **Primary Event:** EVT-IDN-005 — WorkspaceCreated
- **Runtime Projection:** RUN-IDN-005 CreateWorkspaceRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-005
- **Verification Status:** VERIFIED
#### CAP-IDN-006 — InviteMember

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-006
- **Capability Name:** InviteMember
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Initiate membership.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `InviteMember` for `Organization`.
- **Required Inputs:** Person, Organization/Workspace
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Membership Pending
- **Produced References:** OrganizationReference
- **Preconditions:** `Person, Organization` must be available and the applicable policy/authority `Governance Policy` must be resolved.
- **Postconditions:** Membership is pending and auditable.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-006 — InviteMemberCommand
- **Primary Event:** EVT-IDN-006 — MemberInvited
- **Runtime Projection:** RUN-IDN-006 InviteMemberRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-006
- **Verification Status:** VERIFIED
#### CAP-IDN-007 — ActivateMembership

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-007
- **Capability Name:** ActivateMembership
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Activate membership.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ActivateMembership` for `Organization`.
- **Required Inputs:** Membership Pending
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Membership Active
- **Produced References:** OrganizationReference
- **Preconditions:** `Membership` must be available and the applicable policy/authority `Governance Policy` must be resolved.
- **Postconditions:** Membership is active under valid policy.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-007 — ActivateMembershipCommand
- **Primary Event:** EVT-IDN-007 — MembershipActivated
- **Runtime Projection:** RUN-IDN-007 ActivateMembershipRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-007
- **Verification Status:** VERIFIED
#### CAP-IDN-008 — SuspendMembership

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-008
- **Capability Name:** SuspendMembership
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Suspend membership.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `SuspendMembership` for `Organization`.
- **Required Inputs:** Membership Active
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Membership Suspended
- **Produced References:** OrganizationReference
- **Preconditions:** `Membership` must be available and the applicable policy/authority `Governance Policy` must be resolved.
- **Postconditions:** Membership is suspended with rationale.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-008 — SuspendMembershipCommand
- **Primary Event:** EVT-IDN-008 — MembershipSuspended
- **Runtime Projection:** RUN-IDN-008 SuspendMembershipRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-008
- **Verification Status:** VERIFIED
#### CAP-IDN-009 — RevokeMembership

##### Inherited Canonical Core

- **Capability ID:** CAP-IDN-009
- **Capability Name:** RevokeMembership
- **Aggregate Root:** DOM-001 Organization
- **Authority:** Governance Authority
- **Lifecycle:** Organization has `Draft → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-IDN-001, INV-IDN-002, INV-IDN-003, INV-IDN-004, INV-IDN-005, INV-IDN-006
- **Canonical References:** none
- **Derived From:** OES-005 / Identity Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Revoke membership.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `RevokeMembership` for `Organization`.
- **Required Inputs:** Membership Active/Suspended
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Membership Revoked
- **Produced References:** OrganizationReference
- **Preconditions:** `Membership` must be available and the applicable policy/authority `Governance Policy` must be resolved.
- **Postconditions:** Membership no longer grants participation.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-IDN-009 — RevokeMembershipCommand
- **Primary Event:** EVT-IDN-009 — MembershipRevoked
- **Runtime Projection:** RUN-IDN-009 RevokeMembershipRuntimeProjection
- **Traceability:** OES-005::Identity Domain::CAP-IDN-009
- **Verification Status:** VERIFIED

### Knowledge Domain
#### CAP-KNW-001 — CreateKnowledgeAsset

##### Inherited Canonical Core

- **Capability ID:** CAP-KNW-001
- **Capability Name:** CreateKnowledgeAsset
- **Aggregate Root:** DOM-010 KnowledgeAsset
- **Authority:** Knowledge Authority
- **Lifecycle:** `Draft → Validated → Approved → Operational → Archived`
- **Applicable Aggregate Invariants:** INV-KNW-001, INV-KNW-002, INV-KNW-003, INV-KNW-004, INV-KNW-005, INV-KNW-006
- **Canonical References:** none
- **Derived From:** OES-005 / Knowledge Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Register institutional knowledge.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CreateKnowledgeAsset` for `KnowledgeAsset`.
- **Required Inputs:** Source, classification, content reference
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** KnowledgeAsset Draft
- **Produced References:** KnowledgeAssetReference
- **Preconditions:** `Organization` must be available and the applicable policy/authority `Knowledge Policy` must be resolved.
- **Postconditions:** Asset has ID, source and classification.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-KNW-001 — CreateKnowledgeAssetCommand
- **Primary Event:** EVT-KNW-001 — KnowledgeAssetCreated
- **Runtime Projection:** RUN-KNW-001 CreateKnowledgeAssetRuntimeProjection
- **Traceability:** OES-005::Knowledge Domain::CAP-KNW-001
- **Verification Status:** VERIFIED
#### CAP-KNW-002 — ValidateKnowledgeAsset

##### Inherited Canonical Core

- **Capability ID:** CAP-KNW-002
- **Capability Name:** ValidateKnowledgeAsset
- **Aggregate Root:** DOM-010 KnowledgeAsset
- **Authority:** Knowledge Authority
- **Lifecycle:** `Draft → Validated → Approved → Operational → Archived`
- **Applicable Aggregate Invariants:** INV-KNW-001, INV-KNW-002, INV-KNW-003, INV-KNW-004, INV-KNW-005, INV-KNW-006
- **Canonical References:** none
- **Derived From:** OES-005 / Knowledge Domain

##### Behavioral Projection

- **Category:** Validation
- **Purpose:** Validate knowledge quality.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ValidateKnowledgeAsset` for `KnowledgeAsset`.
- **Required Inputs:** KnowledgeAsset Draft
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** KnowledgeAsset Validated
- **Produced References:** KnowledgeAssetReference
- **Preconditions:** `KnowledgeAsset` must be available and the applicable policy/authority `Knowledge Authority` must be resolved.
- **Postconditions:** Validation evidence is recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-KNW-002 — ValidateKnowledgeAssetCommand
- **Primary Event:** EVT-KNW-002 — KnowledgeAssetValidated
- **Runtime Projection:** RUN-KNW-002 ValidateKnowledgeAssetRuntimeProjection
- **Traceability:** OES-005::Knowledge Domain::CAP-KNW-002
- **Verification Status:** VERIFIED
#### CAP-KNW-003 — ApproveKnowledgeAsset

##### Inherited Canonical Core

- **Capability ID:** CAP-KNW-003
- **Capability Name:** ApproveKnowledgeAsset
- **Aggregate Root:** DOM-010 KnowledgeAsset
- **Authority:** Knowledge Authority
- **Lifecycle:** `Draft → Validated → Approved → Operational → Archived`
- **Applicable Aggregate Invariants:** INV-KNW-001, INV-KNW-002, INV-KNW-003, INV-KNW-004, INV-KNW-005, INV-KNW-006
- **Canonical References:** none
- **Derived From:** OES-005 / Knowledge Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Approve institutional use.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ApproveKnowledgeAsset` for `KnowledgeAsset`.
- **Required Inputs:** KnowledgeAsset Validated
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** KnowledgeAsset Approved
- **Produced References:** KnowledgeAssetReference
- **Preconditions:** `Validation` must be available and the applicable policy/authority `Knowledge Authority` must be resolved.
- **Postconditions:** Approval is auditable.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-KNW-003 — ApproveKnowledgeAssetCommand
- **Primary Event:** EVT-KNW-003 — KnowledgeAssetApproved
- **Runtime Projection:** RUN-KNW-003 ApproveKnowledgeAssetRuntimeProjection
- **Traceability:** OES-005::Knowledge Domain::CAP-KNW-003
- **Verification Status:** VERIFIED
#### CAP-KNW-004 — OperationalizeKnowledgeAsset

##### Inherited Canonical Core

- **Capability ID:** CAP-KNW-004
- **Capability Name:** OperationalizeKnowledgeAsset
- **Aggregate Root:** DOM-010 KnowledgeAsset
- **Authority:** Knowledge Authority
- **Lifecycle:** `Draft → Validated → Approved → Operational → Archived`
- **Applicable Aggregate Invariants:** INV-KNW-001, INV-KNW-002, INV-KNW-003, INV-KNW-004, INV-KNW-005, INV-KNW-006
- **Canonical References:** none
- **Derived From:** OES-005 / Knowledge Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Make asset operational.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `OperationalizeKnowledgeAsset` for `KnowledgeAsset`.
- **Required Inputs:** KnowledgeAsset Approved
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** KnowledgeAsset Operational
- **Produced References:** KnowledgeAssetReference
- **Preconditions:** `Approved Asset` must be available and the applicable policy/authority `Knowledge Policy` must be resolved.
- **Postconditions:** Asset is available for authorized use.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-KNW-004 — OperationalizeKnowledgeAssetCommand
- **Primary Event:** EVT-KNW-004 — KnowledgeAssetOperationalized
- **Runtime Projection:** RUN-KNW-004 OperationalizeKnowledgeAssetRuntimeProjection
- **Traceability:** OES-005::Knowledge Domain::CAP-KNW-004
- **Verification Status:** VERIFIED
#### CAP-KNW-005 — ArchiveKnowledgeAsset

##### Inherited Canonical Core

- **Capability ID:** CAP-KNW-005
- **Capability Name:** ArchiveKnowledgeAsset
- **Aggregate Root:** DOM-010 KnowledgeAsset
- **Authority:** Knowledge Authority
- **Lifecycle:** `Draft → Validated → Approved → Operational → Archived`
- **Applicable Aggregate Invariants:** INV-KNW-001, INV-KNW-002, INV-KNW-003, INV-KNW-004, INV-KNW-005, INV-KNW-006
- **Canonical References:** none
- **Derived From:** OES-005 / Knowledge Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Archive asset.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ArchiveKnowledgeAsset` for `KnowledgeAsset`.
- **Required Inputs:** KnowledgeAsset
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** KnowledgeAsset Archived
- **Produced References:** KnowledgeAssetReference
- **Preconditions:** `KnowledgeAsset` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Archived asset retains provenance.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-KNW-005 — ArchiveKnowledgeAssetCommand
- **Primary Event:** EVT-KNW-005 — KnowledgeAssetArchived
- **Runtime Projection:** RUN-KNW-005 ArchiveKnowledgeAssetRuntimeProjection
- **Traceability:** OES-005::Knowledge Domain::CAP-KNW-005
- **Verification Status:** VERIFIED

### Agent Domain
#### CAP-AGT-001 — CreateAgent

##### Inherited Canonical Core

- **Capability ID:** CAP-AGT-001
- **Capability Name:** CreateAgent
- **Aggregate Root:** DOM-020 Agent
- **Authority:** Capability Authority
- **Lifecycle:** `Draft → Approved → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-AGT-001, INV-AGT-002, INV-AGT-003, INV-AGT-004, INV-AGT-005, INV-AGT-006
- **Canonical References:** AuditRecordReference through Observability correlation only
- **Derived From:** OES-005 / Agent Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Create agent profile.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CreateAgent` for `Agent`.
- **Required Inputs:** AgentProfile
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Agent Draft
- **Produced References:** AgentReference
- **Preconditions:** `Workspace` must be available and the applicable policy/authority `Capability Policy` must be resolved.
- **Postconditions:** Agent has identity and profile.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-AGT-001 — CreateAgentCommand
- **Primary Event:** EVT-AGT-001 — AgentCreated
- **Runtime Projection:** RUN-AGT-001 CreateAgentRuntimeProjection
- **Traceability:** OES-005::Agent Domain::CAP-AGT-001
- **Verification Status:** VERIFIED
#### CAP-AGT-002 — ApproveAgent

##### Inherited Canonical Core

- **Capability ID:** CAP-AGT-002
- **Capability Name:** ApproveAgent
- **Aggregate Root:** DOM-020 Agent
- **Authority:** Capability Authority
- **Lifecycle:** `Draft → Approved → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-AGT-001, INV-AGT-002, INV-AGT-003, INV-AGT-004, INV-AGT-005, INV-AGT-006
- **Canonical References:** AuditRecordReference through Observability correlation only
- **Derived From:** OES-005 / Agent Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Approve agent use.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ApproveAgent` for `Agent`.
- **Required Inputs:** Agent Draft
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Agent Approved
- **Produced References:** AgentReference
- **Preconditions:** `Agent` must be available and the applicable policy/authority `Capability Authority` must be resolved.
- **Postconditions:** Approval recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-AGT-002 — ApproveAgentCommand
- **Primary Event:** EVT-AGT-002 — AgentApproved
- **Runtime Projection:** RUN-AGT-002 ApproveAgentRuntimeProjection
- **Traceability:** OES-005::Agent Domain::CAP-AGT-002
- **Verification Status:** VERIFIED
#### CAP-AGT-003 — BindCapability

##### Inherited Canonical Core

- **Capability ID:** CAP-AGT-003
- **Capability Name:** BindCapability
- **Aggregate Root:** DOM-020 Agent
- **Authority:** Capability Authority
- **Lifecycle:** `Draft → Approved → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-AGT-001, INV-AGT-002, INV-AGT-003, INV-AGT-004, INV-AGT-005, INV-AGT-006
- **Canonical References:** AuditRecordReference through Observability correlation only
- **Derived From:** OES-005 / Agent Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Bind authorized capability.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `BindCapability` for `Agent`.
- **Required Inputs:** Agent, Capability
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** CapabilityBinding
- **Produced References:** AgentReference
- **Preconditions:** `Agent, Capability` must be available and the applicable policy/authority `Capability Policy` must be resolved.
- **Postconditions:** Agent can execute bound capability only.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-AGT-003 — BindCapabilityCommand
- **Primary Event:** EVT-AGT-003 — CapabilityBound
- **Runtime Projection:** RUN-AGT-003 BindCapabilityRuntimeProjection
- **Traceability:** OES-005::Agent Domain::CAP-AGT-003
- **Verification Status:** VERIFIED
#### CAP-AGT-004 — ActivateAgent

##### Inherited Canonical Core

- **Capability ID:** CAP-AGT-004
- **Capability Name:** ActivateAgent
- **Aggregate Root:** DOM-020 Agent
- **Authority:** Capability Authority
- **Lifecycle:** `Draft → Approved → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-AGT-001, INV-AGT-002, INV-AGT-003, INV-AGT-004, INV-AGT-005, INV-AGT-006
- **Canonical References:** AuditRecordReference through Observability correlation only
- **Derived From:** OES-005 / Agent Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Activate agent.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ActivateAgent` for `Agent`.
- **Required Inputs:** Agent Approved
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Agent Active
- **Produced References:** AgentReference
- **Preconditions:** `Approved Agent` must be available and the applicable policy/authority `Capability Authority` must be resolved.
- **Postconditions:** Agent active under policy.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-AGT-004 — ActivateAgentCommand
- **Primary Event:** EVT-AGT-004 — AgentActivated
- **Runtime Projection:** RUN-AGT-004 ActivateAgentRuntimeProjection
- **Traceability:** OES-005::Agent Domain::CAP-AGT-004
- **Verification Status:** VERIFIED
#### CAP-AGT-005 — SuspendAgent

##### Inherited Canonical Core

- **Capability ID:** CAP-AGT-005
- **Capability Name:** SuspendAgent
- **Aggregate Root:** DOM-020 Agent
- **Authority:** Capability Authority
- **Lifecycle:** `Draft → Approved → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-AGT-001, INV-AGT-002, INV-AGT-003, INV-AGT-004, INV-AGT-005, INV-AGT-006
- **Canonical References:** AuditRecordReference through Observability correlation only
- **Derived From:** OES-005 / Agent Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Suspend agent.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `SuspendAgent` for `Agent`.
- **Required Inputs:** Agent Active
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Agent Suspended
- **Produced References:** AgentReference
- **Preconditions:** `Agent` must be available and the applicable policy/authority `Capability Authority` must be resolved.
- **Postconditions:** Agent cannot execute capabilities.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-AGT-005 — SuspendAgentCommand
- **Primary Event:** EVT-AGT-005 — AgentSuspended
- **Runtime Projection:** RUN-AGT-005 SuspendAgentRuntimeProjection
- **Traceability:** OES-005::Agent Domain::CAP-AGT-005
- **Verification Status:** VERIFIED
#### CAP-AGT-006 — ArchiveAgent

##### Inherited Canonical Core

- **Capability ID:** CAP-AGT-006
- **Capability Name:** ArchiveAgent
- **Aggregate Root:** DOM-020 Agent
- **Authority:** Capability Authority
- **Lifecycle:** `Draft → Approved → Active → Suspended → Archived`
- **Applicable Aggregate Invariants:** INV-AGT-001, INV-AGT-002, INV-AGT-003, INV-AGT-004, INV-AGT-005, INV-AGT-006
- **Canonical References:** AuditRecordReference through Observability correlation only
- **Derived From:** OES-005 / Agent Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Archive agent.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ArchiveAgent` for `Agent`.
- **Required Inputs:** Agent Suspended/Approved
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Agent Archived
- **Produced References:** AgentReference
- **Preconditions:** `Agent` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Agent remains auditable and inactive.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-AGT-006 — ArchiveAgentCommand
- **Primary Event:** EVT-AGT-006 — AgentArchived
- **Runtime Projection:** RUN-AGT-006 ArchiveAgentRuntimeProjection
- **Traceability:** OES-005::Agent Domain::CAP-AGT-006
- **Verification Status:** VERIFIED

### Conversation Domain
#### CAP-CON-001 — OpenConversation

##### Inherited Canonical Core

- **Capability ID:** CAP-CON-001
- **Capability Name:** OpenConversation
- **Aggregate Root:** DOM-030 Conversation
- **Authority:** Runtime Authority
- **Lifecycle:** `Created → Active → Paused → Active → Closed → Archived`
- **Applicable Aggregate Invariants:** INV-CON-001, INV-CON-002, INV-CON-003, INV-CON-004, INV-CON-005
- **Canonical References:** KnowledgeAssetReference, DecisionReference, ExecutionReference when applicable
- **Derived From:** OES-005 / Conversation Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Start contextual interaction.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `OpenConversation` for `Conversation`.
- **Required Inputs:** Workspace, participant
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Conversation Created
- **Produced References:** ConversationReference
- **Preconditions:** `Workspace` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Conversation has ID and participant.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-CON-001 — OpenConversationCommand
- **Primary Event:** EVT-CON-001 — ConversationCreated
- **Runtime Projection:** RUN-CON-001 OpenConversationRuntimeProjection
- **Traceability:** OES-005::Conversation Domain::CAP-CON-001
- **Verification Status:** VERIFIED
#### CAP-CON-002 — AppendMessage

##### Inherited Canonical Core

- **Capability ID:** CAP-CON-002
- **Capability Name:** AppendMessage
- **Aggregate Root:** DOM-030 Conversation
- **Authority:** Runtime Authority
- **Lifecycle:** `Created → Active → Paused → Active → Closed → Archived`
- **Applicable Aggregate Invariants:** INV-CON-001, INV-CON-002, INV-CON-003, INV-CON-004, INV-CON-005
- **Canonical References:** KnowledgeAssetReference, DecisionReference, ExecutionReference when applicable
- **Derived From:** OES-005 / Conversation Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Record message.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `AppendMessage` for `Conversation`.
- **Required Inputs:** Conversation, message
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Message / Conversation Active
- **Produced References:** ConversationReference
- **Preconditions:** `Conversation` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Message belongs to one Conversation.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-CON-002 — AppendMessageCommand
- **Primary Event:** EVT-CON-002 — MessageRecorded
- **Runtime Projection:** RUN-CON-002 AppendMessageRuntimeProjection
- **Traceability:** OES-005::Conversation Domain::CAP-CON-002
- **Verification Status:** VERIFIED
#### CAP-CON-003 — ResolveContext

##### Inherited Canonical Core

- **Capability ID:** CAP-CON-003
- **Capability Name:** ResolveContext
- **Aggregate Root:** DOM-030 Conversation
- **Authority:** Runtime Authority
- **Lifecycle:** `Created → Active → Paused → Active → Closed → Archived`
- **Applicable Aggregate Invariants:** INV-CON-001, INV-CON-002, INV-CON-003, INV-CON-004, INV-CON-005
- **Canonical References:** KnowledgeAssetReference, DecisionReference, ExecutionReference when applicable
- **Derived From:** OES-005 / Conversation Domain

##### Behavioral Projection

- **Category:** Coordination
- **Purpose:** Resolve active context.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ResolveContext` for `Conversation`.
- **Required Inputs:** Conversation
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** ContextSnapshot
- **Produced References:** ConversationReference
- **Preconditions:** `Conversation, Knowledge refs` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Context is consistent and authorized.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-CON-003 — ResolveContextCommand
- **Primary Event:** EVT-CON-003 — ContextResolved
- **Runtime Projection:** RUN-CON-003 ResolveContextRuntimeProjection
- **Traceability:** OES-005::Conversation Domain::CAP-CON-003
- **Verification Status:** VERIFIED
#### CAP-CON-004 — PauseConversation

##### Inherited Canonical Core

- **Capability ID:** CAP-CON-004
- **Capability Name:** PauseConversation
- **Aggregate Root:** DOM-030 Conversation
- **Authority:** Runtime Authority
- **Lifecycle:** `Created → Active → Paused → Active → Closed → Archived`
- **Applicable Aggregate Invariants:** INV-CON-001, INV-CON-002, INV-CON-003, INV-CON-004, INV-CON-005
- **Canonical References:** KnowledgeAssetReference, DecisionReference, ExecutionReference when applicable
- **Derived From:** OES-005 / Conversation Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Pause interaction.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `PauseConversation` for `Conversation`.
- **Required Inputs:** Conversation Active
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Conversation Paused
- **Produced References:** ConversationReference
- **Preconditions:** `Conversation` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Conversation cannot accept normal messages.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-CON-004 — PauseConversationCommand
- **Primary Event:** EVT-CON-004 — ConversationPaused
- **Runtime Projection:** RUN-CON-004 PauseConversationRuntimeProjection
- **Traceability:** OES-005::Conversation Domain::CAP-CON-004
- **Verification Status:** VERIFIED
#### CAP-CON-005 — ResumeConversation

##### Inherited Canonical Core

- **Capability ID:** CAP-CON-005
- **Capability Name:** ResumeConversation
- **Aggregate Root:** DOM-030 Conversation
- **Authority:** Runtime Authority
- **Lifecycle:** `Created → Active → Paused → Active → Closed → Archived`
- **Applicable Aggregate Invariants:** INV-CON-001, INV-CON-002, INV-CON-003, INV-CON-004, INV-CON-005
- **Canonical References:** KnowledgeAssetReference, DecisionReference, ExecutionReference when applicable
- **Derived From:** OES-005 / Conversation Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Resume interaction.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ResumeConversation` for `Conversation`.
- **Required Inputs:** Conversation Paused
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Conversation Active
- **Produced References:** ConversationReference
- **Preconditions:** `Conversation` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Conversation is active again.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-CON-005 — ResumeConversationCommand
- **Primary Event:** EVT-CON-005 — ConversationResumed
- **Runtime Projection:** RUN-CON-005 ResumeConversationRuntimeProjection
- **Traceability:** OES-005::Conversation Domain::CAP-CON-005
- **Verification Status:** VERIFIED
#### CAP-CON-006 — CloseConversation

##### Inherited Canonical Core

- **Capability ID:** CAP-CON-006
- **Capability Name:** CloseConversation
- **Aggregate Root:** DOM-030 Conversation
- **Authority:** Runtime Authority
- **Lifecycle:** `Created → Active → Paused → Active → Closed → Archived`
- **Applicable Aggregate Invariants:** INV-CON-001, INV-CON-002, INV-CON-003, INV-CON-004, INV-CON-005
- **Canonical References:** KnowledgeAssetReference, DecisionReference, ExecutionReference when applicable
- **Derived From:** OES-005 / Conversation Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Close interaction.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CloseConversation` for `Conversation`.
- **Required Inputs:** Conversation Active/Paused
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Conversation Closed
- **Produced References:** ConversationReference
- **Preconditions:** `Conversation` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Conversation cannot accept normal messages.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-CON-006 — CloseConversationCommand
- **Primary Event:** EVT-CON-006 — ConversationClosed
- **Runtime Projection:** RUN-CON-006 CloseConversationRuntimeProjection
- **Traceability:** OES-005::Conversation Domain::CAP-CON-006
- **Verification Status:** VERIFIED
#### CAP-CON-007 — ArchiveConversation

##### Inherited Canonical Core

- **Capability ID:** CAP-CON-007
- **Capability Name:** ArchiveConversation
- **Aggregate Root:** DOM-030 Conversation
- **Authority:** Runtime Authority
- **Lifecycle:** `Created → Active → Paused → Active → Closed → Archived`
- **Applicable Aggregate Invariants:** INV-CON-001, INV-CON-002, INV-CON-003, INV-CON-004, INV-CON-005
- **Canonical References:** KnowledgeAssetReference, DecisionReference, ExecutionReference when applicable
- **Derived From:** OES-005 / Conversation Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Archive context.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ArchiveConversation` for `Conversation`.
- **Required Inputs:** Conversation Closed
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Conversation Archived
- **Produced References:** ConversationReference
- **Preconditions:** `Conversation` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Context remains retrievable by policy.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-CON-007 — ArchiveConversationCommand
- **Primary Event:** EVT-CON-007 — ConversationArchived
- **Runtime Projection:** RUN-CON-007 ArchiveConversationRuntimeProjection
- **Traceability:** OES-005::Conversation Domain::CAP-CON-007
- **Verification Status:** VERIFIED

### Decision Domain
#### CAP-DEC-001 — CreateDecision

##### Inherited Canonical Core

- **Capability ID:** CAP-DEC-001
- **Capability Name:** CreateDecision
- **Aggregate Root:** DOM-040 Decision
- **Authority:** Decision Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-DEC-001, INV-DEC-002, INV-DEC-003, INV-DEC-004, INV-DEC-005, INV-DEC-006, INV-DEC-007, INV-DEC-008
- **Canonical References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference
- **Derived From:** OES-005 / Decision Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Create draft decision.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CreateDecision` for `Decision`.
- **Required Inputs:** Context, rationale draft
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Decision Draft
- **Produced References:** DecisionReference
- **Preconditions:** `Conversation/Knowledge` must be available and the applicable policy/authority `Decision Policy` must be resolved.
- **Postconditions:** Draft has ID and context.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-DEC-001 — CreateDecisionCommand
- **Primary Event:** EVT-DEC-001 — DecisionCreated
- **Runtime Projection:** RUN-DEC-001 CreateDecisionRuntimeProjection
- **Traceability:** OES-005::Decision Domain::CAP-DEC-001
- **Verification Status:** VERIFIED
#### CAP-DEC-002 — AttachEvidence

##### Inherited Canonical Core

- **Capability ID:** CAP-DEC-002
- **Capability Name:** AttachEvidence
- **Aggregate Root:** DOM-040 Decision
- **Authority:** Decision Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-DEC-001, INV-DEC-002, INV-DEC-003, INV-DEC-004, INV-DEC-005, INV-DEC-006, INV-DEC-007, INV-DEC-008
- **Canonical References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference
- **Derived From:** OES-005 / Decision Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Attach admissible evidence reference.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `AttachEvidence` for `Decision`.
- **Required Inputs:** Decision, EvidenceReference
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Decision with Evidence
- **Produced References:** EvidenceReference
- **Preconditions:** `Evidence owner` must be available and the applicable policy/authority `Decision Policy` must be resolved.
- **Postconditions:** EvidenceReference is valid and owned.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-DEC-002 — AttachEvidenceCommand
- **Primary Event:** EVT-DEC-002 — EvidenceAttached
- **Runtime Projection:** RUN-DEC-002 AttachEvidenceRuntimeProjection
- **Traceability:** OES-005::Decision Domain::CAP-DEC-002
- **Verification Status:** VERIFIED
#### CAP-DEC-003 — SubmitDecisionReview

##### Inherited Canonical Core

- **Capability ID:** CAP-DEC-003
- **Capability Name:** SubmitDecisionReview
- **Aggregate Root:** DOM-040 Decision
- **Authority:** Decision Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-DEC-001, INV-DEC-002, INV-DEC-003, INV-DEC-004, INV-DEC-005, INV-DEC-006, INV-DEC-007, INV-DEC-008
- **Canonical References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference
- **Derived From:** OES-005 / Decision Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Submit for review.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `SubmitDecisionReview` for `Decision`.
- **Required Inputs:** Decision Draft
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Decision Under Review
- **Produced References:** DecisionReference
- **Preconditions:** `Evidence, Rationale` must be available and the applicable policy/authority `Decision Policy` must be resolved.
- **Postconditions:** Decision has minimum evidence and rationale.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-DEC-003 — SubmitDecisionReviewCommand
- **Primary Event:** EVT-DEC-003 — DecisionSubmitted
- **Runtime Projection:** RUN-DEC-003 SubmitDecisionReviewRuntimeProjection
- **Traceability:** OES-005::Decision Domain::CAP-DEC-003
- **Verification Status:** VERIFIED
#### CAP-DEC-004 — ApproveDecision

##### Inherited Canonical Core

- **Capability ID:** CAP-DEC-004
- **Capability Name:** ApproveDecision
- **Aggregate Root:** DOM-040 Decision
- **Authority:** Decision Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-DEC-001, INV-DEC-002, INV-DEC-003, INV-DEC-004, INV-DEC-005, INV-DEC-006, INV-DEC-007, INV-DEC-008
- **Canonical References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference
- **Derived From:** OES-005 / Decision Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Approve decision.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ApproveDecision` for `Decision`.
- **Required Inputs:** Decision Under Review
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Decision Approved
- **Produced References:** DecisionReference
- **Preconditions:** `Review` must be available and the applicable policy/authority `Decision Authority` must be resolved.
- **Postconditions:** Approval is recorded; content immutable.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-DEC-004 — ApproveDecisionCommand
- **Primary Event:** EVT-DEC-004 — DecisionApproved
- **Runtime Projection:** RUN-DEC-004 ApproveDecisionRuntimeProjection
- **Traceability:** OES-005::Decision Domain::CAP-DEC-004
- **Verification Status:** VERIFIED
#### CAP-DEC-005 — RejectDecision

##### Inherited Canonical Core

- **Capability ID:** CAP-DEC-005
- **Capability Name:** RejectDecision
- **Aggregate Root:** DOM-040 Decision
- **Authority:** Decision Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-DEC-001, INV-DEC-002, INV-DEC-003, INV-DEC-004, INV-DEC-005, INV-DEC-006, INV-DEC-007, INV-DEC-008
- **Canonical References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference
- **Derived From:** OES-005 / Decision Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Reject decision.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `RejectDecision` for `Decision`.
- **Required Inputs:** Decision Under Review
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Decision Rejected
- **Produced References:** DecisionReference
- **Preconditions:** `Review` must be available and the applicable policy/authority `Decision Authority` must be resolved.
- **Postconditions:** Rejection rationale is recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-DEC-005 — RejectDecisionCommand
- **Primary Event:** EVT-DEC-005 — DecisionRejected
- **Runtime Projection:** RUN-DEC-005 RejectDecisionRuntimeProjection
- **Traceability:** OES-005::Decision Domain::CAP-DEC-005
- **Verification Status:** VERIFIED
#### CAP-DEC-006 — PublishDecision

##### Inherited Canonical Core

- **Capability ID:** CAP-DEC-006
- **Capability Name:** PublishDecision
- **Aggregate Root:** DOM-040 Decision
- **Authority:** Decision Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-DEC-001, INV-DEC-002, INV-DEC-003, INV-DEC-004, INV-DEC-005, INV-DEC-006, INV-DEC-007, INV-DEC-008
- **Canonical References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference
- **Derived From:** OES-005 / Decision Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Make effective.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `PublishDecision` for `Decision`.
- **Required Inputs:** Decision Approved
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Decision Effective
- **Produced References:** DecisionReference
- **Preconditions:** `Approval` must be available and the applicable policy/authority `Decision Policy` must be resolved.
- **Postconditions:** EffectiveDate is recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-DEC-006 — PublishDecisionCommand
- **Primary Event:** EVT-DEC-006 — DecisionPublished
- **Runtime Projection:** RUN-DEC-006 PublishDecisionRuntimeProjection
- **Traceability:** OES-005::Decision Domain::CAP-DEC-006
- **Verification Status:** VERIFIED
#### CAP-DEC-007 — SupersedeDecision

##### Inherited Canonical Core

- **Capability ID:** CAP-DEC-007
- **Capability Name:** SupersedeDecision
- **Aggregate Root:** DOM-040 Decision
- **Authority:** Decision Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-DEC-001, INV-DEC-002, INV-DEC-003, INV-DEC-004, INV-DEC-005, INV-DEC-006, INV-DEC-007, INV-DEC-008
- **Canonical References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference
- **Derived From:** OES-005 / Decision Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Replace decision.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `SupersedeDecision` for `Decision`.
- **Required Inputs:** Decision Effective, new Decision
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Decision Superseded
- **Produced References:** DecisionReference
- **Preconditions:** `New Decision` must be available and the applicable policy/authority `Decision Authority` must be resolved.
- **Postconditions:** Supersession reference is recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-DEC-007 — SupersedeDecisionCommand
- **Primary Event:** EVT-DEC-007 — DecisionSuperseded
- **Runtime Projection:** RUN-DEC-007 SupersedeDecisionRuntimeProjection
- **Traceability:** OES-005::Decision Domain::CAP-DEC-007
- **Verification Status:** VERIFIED
#### CAP-DEC-008 — ArchiveDecision

##### Inherited Canonical Core

- **Capability ID:** CAP-DEC-008
- **Capability Name:** ArchiveDecision
- **Aggregate Root:** DOM-040 Decision
- **Authority:** Decision Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-DEC-001, INV-DEC-002, INV-DEC-003, INV-DEC-004, INV-DEC-005, INV-DEC-006, INV-DEC-007, INV-DEC-008
- **Canonical References:** ConversationReference, KnowledgeAssetReference, ExecutionReference, AuditRecordReference
- **Derived From:** OES-005 / Decision Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Archive decision.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ArchiveDecision` for `Decision`.
- **Required Inputs:** Decision terminal
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Decision Archived
- **Produced References:** DecisionReference
- **Preconditions:** `Decision` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Decision remains auditable.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-DEC-008 — ArchiveDecisionCommand
- **Primary Event:** EVT-DEC-008 — DecisionArchived
- **Runtime Projection:** RUN-DEC-008 ArchiveDecisionRuntimeProjection
- **Traceability:** OES-005::Decision Domain::CAP-DEC-008
- **Verification Status:** VERIFIED

### Execution Domain
#### CAP-EXE-001 — PlanExecution

##### Inherited Canonical Core

- **Capability ID:** CAP-EXE-001
- **Capability Name:** PlanExecution
- **Aggregate Root:** DOM-050 Execution
- **Authority:** Runtime Authority
- **Lifecycle:** `Planned → Authorized → Running → Completed → Verified → Archived`
- **Applicable Aggregate Invariants:** INV-EXE-001, INV-EXE-002, INV-EXE-003, INV-EXE-004, INV-EXE-005, INV-EXE-006, INV-EXE-007
- **Canonical References:** DecisionReference, PolicyReference, KnowledgeAssetReference, AuditRecordReference
- **Derived From:** OES-005 / Execution Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Plan execution from authorizer.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `PlanExecution` for `Execution`.
- **Required Inputs:** Decision/Policy
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Execution Planned
- **Produced References:** ExecutionReference
- **Preconditions:** `Decision/Policy` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Plan references authorizer.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-EXE-001 — PlanExecutionCommand
- **Primary Event:** EVT-EXE-001 — ExecutionPlanned
- **Runtime Projection:** RUN-EXE-001 PlanExecutionRuntimeProjection
- **Traceability:** OES-005::Execution Domain::CAP-EXE-001
- **Verification Status:** VERIFIED
#### CAP-EXE-002 — AuthorizeExecution

##### Inherited Canonical Core

- **Capability ID:** CAP-EXE-002
- **Capability Name:** AuthorizeExecution
- **Aggregate Root:** DOM-050 Execution
- **Authority:** Runtime Authority
- **Lifecycle:** `Planned → Authorized → Running → Completed → Verified → Archived`
- **Applicable Aggregate Invariants:** INV-EXE-001, INV-EXE-002, INV-EXE-003, INV-EXE-004, INV-EXE-005, INV-EXE-006, INV-EXE-007
- **Canonical References:** DecisionReference, PolicyReference, KnowledgeAssetReference, AuditRecordReference
- **Derived From:** OES-005 / Execution Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Authorize execution.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `AuthorizeExecution` for `Execution`.
- **Required Inputs:** Execution Planned
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Execution Authorized
- **Produced References:** ExecutionReference
- **Preconditions:** `Plan` must be available and the applicable policy/authority `Runtime Authority` must be resolved.
- **Postconditions:** Authorization recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-EXE-002 — AuthorizeExecutionCommand
- **Primary Event:** EVT-EXE-002 — ExecutionAuthorized
- **Runtime Projection:** RUN-EXE-002 AuthorizeExecutionRuntimeProjection
- **Traceability:** OES-005::Execution Domain::CAP-EXE-002
- **Verification Status:** VERIFIED
#### CAP-EXE-003 — StartExecution

##### Inherited Canonical Core

- **Capability ID:** CAP-EXE-003
- **Capability Name:** StartExecution
- **Aggregate Root:** DOM-050 Execution
- **Authority:** Runtime Authority
- **Lifecycle:** `Planned → Authorized → Running → Completed → Verified → Archived`
- **Applicable Aggregate Invariants:** INV-EXE-001, INV-EXE-002, INV-EXE-003, INV-EXE-004, INV-EXE-005, INV-EXE-006, INV-EXE-007
- **Canonical References:** DecisionReference, PolicyReference, KnowledgeAssetReference, AuditRecordReference
- **Derived From:** OES-005 / Execution Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Start execution.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `StartExecution` for `Execution`.
- **Required Inputs:** Execution Authorized
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Execution Running
- **Produced References:** ExecutionReference
- **Preconditions:** `Authorization` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Running state recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-EXE-003 — StartExecutionCommand
- **Primary Event:** EVT-EXE-003 — ExecutionStarted
- **Runtime Projection:** RUN-EXE-003 StartExecutionRuntimeProjection
- **Traceability:** OES-005::Execution Domain::CAP-EXE-003
- **Verification Status:** VERIFIED
#### CAP-EXE-004 — CompleteExecution

##### Inherited Canonical Core

- **Capability ID:** CAP-EXE-004
- **Capability Name:** CompleteExecution
- **Aggregate Root:** DOM-050 Execution
- **Authority:** Runtime Authority
- **Lifecycle:** `Planned → Authorized → Running → Completed → Verified → Archived`
- **Applicable Aggregate Invariants:** INV-EXE-001, INV-EXE-002, INV-EXE-003, INV-EXE-004, INV-EXE-005, INV-EXE-006, INV-EXE-007
- **Canonical References:** DecisionReference, PolicyReference, KnowledgeAssetReference, AuditRecordReference
- **Derived From:** OES-005 / Execution Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Complete execution.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CompleteExecution` for `Execution`.
- **Required Inputs:** Execution Running
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Execution Completed
- **Produced References:** ExecutionReference
- **Preconditions:** `Tasks` must be available and the applicable policy/authority `Runtime Policy` must be resolved.
- **Postconditions:** Result and ExecutionEvidence recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-EXE-004 — CompleteExecutionCommand
- **Primary Event:** EVT-EXE-004 — ExecutionCompleted
- **Runtime Projection:** RUN-EXE-004 CompleteExecutionRuntimeProjection
- **Traceability:** OES-005::Execution Domain::CAP-EXE-004
- **Verification Status:** VERIFIED
#### CAP-EXE-005 — VerifyExecution

##### Inherited Canonical Core

- **Capability ID:** CAP-EXE-005
- **Capability Name:** VerifyExecution
- **Aggregate Root:** DOM-050 Execution
- **Authority:** Runtime Authority
- **Lifecycle:** `Planned → Authorized → Running → Completed → Verified → Archived`
- **Applicable Aggregate Invariants:** INV-EXE-001, INV-EXE-002, INV-EXE-003, INV-EXE-004, INV-EXE-005, INV-EXE-006, INV-EXE-007
- **Canonical References:** DecisionReference, PolicyReference, KnowledgeAssetReference, AuditRecordReference
- **Derived From:** OES-005 / Execution Domain

##### Behavioral Projection

- **Category:** Validation
- **Purpose:** Verify result.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `VerifyExecution` for `Execution`.
- **Required Inputs:** Execution Completed
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Execution Verified
- **Produced References:** ExecutionReference
- **Preconditions:** `Result, Evidence` must be available and the applicable policy/authority `Runtime Authority` must be resolved.
- **Postconditions:** ExecutionEvidence exists.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-EXE-005 — VerifyExecutionCommand
- **Primary Event:** EVT-EXE-005 — ExecutionVerified
- **Runtime Projection:** RUN-EXE-005 VerifyExecutionRuntimeProjection
- **Traceability:** OES-005::Execution Domain::CAP-EXE-005
- **Verification Status:** VERIFIED
#### CAP-EXE-006 — ArchiveExecution

##### Inherited Canonical Core

- **Capability ID:** CAP-EXE-006
- **Capability Name:** ArchiveExecution
- **Aggregate Root:** DOM-050 Execution
- **Authority:** Runtime Authority
- **Lifecycle:** `Planned → Authorized → Running → Completed → Verified → Archived`
- **Applicable Aggregate Invariants:** INV-EXE-001, INV-EXE-002, INV-EXE-003, INV-EXE-004, INV-EXE-005, INV-EXE-006, INV-EXE-007
- **Canonical References:** DecisionReference, PolicyReference, KnowledgeAssetReference, AuditRecordReference
- **Derived From:** OES-005 / Execution Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Archive execution.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ArchiveExecution` for `Execution`.
- **Required Inputs:** Execution Verified
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Execution Archived
- **Produced References:** ExecutionReference
- **Preconditions:** `Execution` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Audit trail preserved.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-EXE-006 — ArchiveExecutionCommand
- **Primary Event:** EVT-EXE-006 — ExecutionArchived
- **Runtime Projection:** RUN-EXE-006 ArchiveExecutionRuntimeProjection
- **Traceability:** OES-005::Execution Domain::CAP-EXE-006
- **Verification Status:** VERIFIED
#### CAP-EXE-007 — PromoteArtifactToKnowledge

##### Inherited Canonical Core

- **Capability ID:** CAP-EXE-007
- **Capability Name:** PromoteArtifactToKnowledge
- **Aggregate Root:** DOM-050 Execution
- **Authority:** Runtime Authority
- **Lifecycle:** `Planned → Authorized → Running → Completed → Verified → Archived`
- **Applicable Aggregate Invariants:** INV-EXE-001, INV-EXE-002, INV-EXE-003, INV-EXE-004, INV-EXE-005, INV-EXE-006, INV-EXE-007
- **Canonical References:** DecisionReference, PolicyReference, KnowledgeAssetReference, AuditRecordReference
- **Derived From:** OES-005 / Execution Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Request artifact promotion.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `PromoteArtifactToKnowledge` for `Execution`.
- **Required Inputs:** Artifact, provenance
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** KnowledgeAsset Draft
- **Produced References:** KnowledgeAssetReference
- **Preconditions:** `Execution Artifact` must be available and the applicable policy/authority `Knowledge Authority` must be resolved.
- **Postconditions:** Promotion creates KnowledgeAsset via Knowledge capability.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-EXE-007 — PromoteArtifactToKnowledgeCommand
- **Primary Event:** EVT-EXE-007 — ExecutionArtifactProduced
- **Runtime Projection:** RUN-EXE-007 PromoteArtifactToKnowledgeRuntimeProjection
- **Traceability:** OES-005::Execution Domain::CAP-EXE-007
- **Verification Status:** VERIFIED

### Governance Domain
#### CAP-GOV-001 — CreatePolicy

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-001
- **Capability Name:** CreatePolicy
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Create draft policy.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CreatePolicy` for `Policy`.
- **Required Inputs:** Scope, rules draft
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Policy Draft
- **Produced References:** PolicyReference
- **Preconditions:** `Organization` must be available and the applicable policy/authority `Governance Policy` must be resolved.
- **Postconditions:** Policy has ID and scope.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-001 — CreatePolicyCommand
- **Primary Event:** EVT-GOV-001 — PolicyCreated
- **Runtime Projection:** RUN-GOV-001 CreatePolicyRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-001
- **Verification Status:** VERIFIED
#### CAP-GOV-002 — SubmitPolicyReview

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-002
- **Capability Name:** SubmitPolicyReview
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Submit policy for review.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `SubmitPolicyReview` for `Policy`.
- **Required Inputs:** Policy Draft
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Policy Under Review
- **Produced References:** PolicyReference
- **Preconditions:** `Policy` must be available and the applicable policy/authority `Governance Policy` must be resolved.
- **Postconditions:** Review state recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-002 — SubmitPolicyReviewCommand
- **Primary Event:** EVT-GOV-002 — PolicySubmitted
- **Runtime Projection:** RUN-GOV-002 SubmitPolicyReviewRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-002
- **Verification Status:** VERIFIED
#### CAP-GOV-003 — ApprovePolicy

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-003
- **Capability Name:** ApprovePolicy
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Approve policy.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ApprovePolicy` for `Policy`.
- **Required Inputs:** Policy Under Review
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Policy Approved
- **Produced References:** PolicyReference
- **Preconditions:** `Review` must be available and the applicable policy/authority `Governance Authority` must be resolved.
- **Postconditions:** Approval recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-003 — ApprovePolicyCommand
- **Primary Event:** EVT-GOV-003 — PolicyApproved
- **Runtime Projection:** RUN-GOV-003 ApprovePolicyRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-003
- **Verification Status:** VERIFIED
#### CAP-GOV-004 — RejectPolicy

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-004
- **Capability Name:** RejectPolicy
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Reject policy.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `RejectPolicy` for `Policy`.
- **Required Inputs:** Policy Under Review
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Policy Rejected
- **Produced References:** PolicyReference
- **Preconditions:** `Review` must be available and the applicable policy/authority `Governance Authority` must be resolved.
- **Postconditions:** Rejection rationale recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-004 — RejectPolicyCommand
- **Primary Event:** EVT-GOV-004 — PolicyRejected
- **Runtime Projection:** RUN-GOV-004 RejectPolicyRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-004
- **Verification Status:** VERIFIED
#### CAP-GOV-005 — PublishPolicy

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-005
- **Capability Name:** PublishPolicy
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Make policy effective.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `PublishPolicy` for `Policy`.
- **Required Inputs:** Policy Approved
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Policy Effective
- **Produced References:** PolicyReference
- **Preconditions:** `Approval` must be available and the applicable policy/authority `Governance Authority` must be resolved.
- **Postconditions:** Effective period recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-005 — PublishPolicyCommand
- **Primary Event:** EVT-GOV-005 — PolicyPublished
- **Runtime Projection:** RUN-GOV-005 PublishPolicyRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-005
- **Verification Status:** VERIFIED
#### CAP-GOV-006 — SupersedePolicy

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-006
- **Capability Name:** SupersedePolicy
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Supersede effective policy.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `SupersedePolicy` for `Policy`.
- **Required Inputs:** Policy Effective, new Policy
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Policy Superseded
- **Produced References:** PolicyReference
- **Preconditions:** `New Policy` must be available and the applicable policy/authority `Governance Authority` must be resolved.
- **Postconditions:** Supersession reference recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-006 — SupersedePolicyCommand
- **Primary Event:** EVT-GOV-006 — PolicySuperseded
- **Runtime Projection:** RUN-GOV-006 SupersedePolicyRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-006
- **Verification Status:** VERIFIED
#### CAP-GOV-007 — DelegateAuthority

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-007
- **Capability Name:** DelegateAuthority
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Grant delegation.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `DelegateAuthority` for `Policy`.
- **Required Inputs:** Authority, delegate, scope
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Delegation
- **Produced References:** PolicyReference
- **Preconditions:** `Policy` must be available and the applicable policy/authority `Governance Authority` must be resolved.
- **Postconditions:** Delegation has explicit validity.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-007 — DelegateAuthorityCommand
- **Primary Event:** EVT-GOV-007 — DelegationGranted
- **Runtime Projection:** RUN-GOV-007 DelegateAuthorityRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-007
- **Verification Status:** VERIFIED
#### CAP-GOV-008 — RevokeDelegation

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-008
- **Capability Name:** RevokeDelegation
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Governance
- **Purpose:** Revoke delegation.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `RevokeDelegation` for `Policy`.
- **Required Inputs:** Delegation
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Delegation Revoked
- **Produced References:** PolicyReference
- **Preconditions:** `Delegation` must be available and the applicable policy/authority `Governance Authority` must be resolved.
- **Postconditions:** Revocation recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-008 — RevokeDelegationCommand
- **Primary Event:** EVT-GOV-008 — DelegationRevoked
- **Runtime Projection:** RUN-GOV-008 RevokeDelegationRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-008
- **Verification Status:** VERIFIED
#### CAP-GOV-009 — ArchivePolicy

##### Inherited Canonical Core

- **Capability ID:** CAP-GOV-009
- **Capability Name:** ArchivePolicy
- **Aggregate Root:** DOM-060 Policy
- **Authority:** Governance Authority
- **Lifecycle:** `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived`
- **Applicable Aggregate Invariants:** INV-GOV-001, INV-GOV-002, INV-GOV-003, INV-GOV-004, INV-GOV-005, INV-GOV-006, INV-GOV-007
- **Canonical References:** OrganizationReference, WorkspaceReference, AgentReference, CapabilityReference, DecisionReference, ExecutionReference
- **Derived From:** OES-005 / Governance Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Archive policy.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ArchivePolicy` for `Policy`.
- **Required Inputs:** Policy terminal
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Policy Archived
- **Produced References:** PolicyReference
- **Preconditions:** `Policy` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Policy remains auditable.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-GOV-009 — ArchivePolicyCommand
- **Primary Event:** EVT-GOV-009 — PolicyArchived
- **Runtime Projection:** RUN-GOV-009 ArchivePolicyRuntimeProjection
- **Traceability:** OES-005::Governance Domain::CAP-GOV-009
- **Verification Status:** VERIFIED

### Observability Domain
#### CAP-OBS-001 — RegisterAuditRecord

##### Inherited Canonical Core

- **Capability ID:** CAP-OBS-001
- **Capability Name:** RegisterAuditRecord
- **Aggregate Root:** DOM-070 AuditRecord
- **Authority:** Observability Authority
- **Lifecycle:** `Registered → Validated → Retained → Archived`
- **Applicable Aggregate Invariants:** INV-OBS-001, INV-OBS-002, INV-OBS-003, INV-OBS-004, INV-OBS-005, INV-OBS-006, INV-OBS-007
- **Canonical References:** DecisionReference, ExecutionReference, KnowledgeAssetReference, PolicyReference
- **Derived From:** OES-005 / Observability Domain

##### Behavioral Projection

- **Category:** Operational
- **Purpose:** Register evidence.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `RegisterAuditRecord` for `AuditRecord`.
- **Required Inputs:** Context, evidence
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** AuditRecord Registered
- **Produced References:** AuditRecordReference
- **Preconditions:** `Origin aggregate` must be available and the applicable policy/authority `Observability Policy` must be resolved.
- **Postconditions:** Record payload is immutable and correlated.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-OBS-001 — RegisterAuditRecordCommand
- **Primary Event:** EVT-OBS-001 — AuditRecordRegistered
- **Runtime Projection:** RUN-OBS-001 RegisterAuditRecordRuntimeProjection
- **Traceability:** OES-005::Observability Domain::CAP-OBS-001
- **Verification Status:** VERIFIED
#### CAP-OBS-002 — ValidateEvidence

##### Inherited Canonical Core

- **Capability ID:** CAP-OBS-002
- **Capability Name:** ValidateEvidence
- **Aggregate Root:** DOM-070 AuditRecord
- **Authority:** Observability Authority
- **Lifecycle:** `Registered → Validated → Retained → Archived`
- **Applicable Aggregate Invariants:** INV-OBS-001, INV-OBS-002, INV-OBS-003, INV-OBS-004, INV-OBS-005, INV-OBS-006, INV-OBS-007
- **Canonical References:** DecisionReference, ExecutionReference, KnowledgeAssetReference, PolicyReference
- **Derived From:** OES-005 / Observability Domain

##### Behavioral Projection

- **Category:** Validation
- **Purpose:** Validate evidence.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ValidateEvidence` for `AuditRecord`.
- **Required Inputs:** AuditRecord
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** AuditRecord Validated
- **Produced References:** AuditRecordReference
- **Preconditions:** `AuditRecord` must be available and the applicable policy/authority `Observability Authority` must be resolved.
- **Postconditions:** Validation metadata recorded.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-OBS-002 — ValidateEvidenceCommand
- **Primary Event:** EVT-OBS-002 — EvidenceValidated
- **Runtime Projection:** RUN-OBS-002 ValidateEvidenceRuntimeProjection
- **Traceability:** OES-005::Observability Domain::CAP-OBS-002
- **Verification Status:** VERIFIED
#### CAP-OBS-003 — CorrelateEvidence

##### Inherited Canonical Core

- **Capability ID:** CAP-OBS-003
- **Capability Name:** CorrelateEvidence
- **Aggregate Root:** DOM-070 AuditRecord
- **Authority:** Observability Authority
- **Lifecycle:** `Registered → Validated → Retained → Archived`
- **Applicable Aggregate Invariants:** INV-OBS-001, INV-OBS-002, INV-OBS-003, INV-OBS-004, INV-OBS-005, INV-OBS-006, INV-OBS-007
- **Canonical References:** DecisionReference, ExecutionReference, KnowledgeAssetReference, PolicyReference
- **Derived From:** OES-005 / Observability Domain

##### Behavioral Projection

- **Category:** Coordination
- **Purpose:** Correlate records.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `CorrelateEvidence` for `AuditRecord`.
- **Required Inputs:** AuditRecords
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** Correlation
- **Produced References:** AuditRecordReference
- **Preconditions:** `Records` must be available and the applicable policy/authority `Observability Policy` must be resolved.
- **Postconditions:** Correlation references origins.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-OBS-003 — CorrelateEvidenceCommand
- **Primary Event:** EVT-OBS-003 — EvidenceCorrelated
- **Runtime Projection:** RUN-OBS-003 CorrelateEvidenceRuntimeProjection
- **Traceability:** OES-005::Observability Domain::CAP-OBS-003
- **Verification Status:** VERIFIED
#### CAP-OBS-004 — ApplyRetentionPolicy

##### Inherited Canonical Core

- **Capability ID:** CAP-OBS-004
- **Capability Name:** ApplyRetentionPolicy
- **Aggregate Root:** DOM-070 AuditRecord
- **Authority:** Observability Authority
- **Lifecycle:** `Registered → Validated → Retained → Archived`
- **Applicable Aggregate Invariants:** INV-OBS-001, INV-OBS-002, INV-OBS-003, INV-OBS-004, INV-OBS-005, INV-OBS-006, INV-OBS-007
- **Canonical References:** DecisionReference, ExecutionReference, KnowledgeAssetReference, PolicyReference
- **Derived From:** OES-005 / Observability Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Apply retention.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ApplyRetentionPolicy` for `AuditRecord`.
- **Required Inputs:** AuditRecord
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** AuditRecord Retained
- **Produced References:** AuditRecordReference
- **Preconditions:** `Policy` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Retention class applied.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-OBS-004 — ApplyRetentionPolicyCommand
- **Primary Event:** EVT-OBS-004 — RetentionApplied
- **Runtime Projection:** RUN-OBS-004 ApplyRetentionPolicyRuntimeProjection
- **Traceability:** OES-005::Observability Domain::CAP-OBS-004
- **Verification Status:** VERIFIED
#### CAP-OBS-005 — ArchiveEvidence

##### Inherited Canonical Core

- **Capability ID:** CAP-OBS-005
- **Capability Name:** ArchiveEvidence
- **Aggregate Root:** DOM-070 AuditRecord
- **Authority:** Observability Authority
- **Lifecycle:** `Registered → Validated → Retained → Archived`
- **Applicable Aggregate Invariants:** INV-OBS-001, INV-OBS-002, INV-OBS-003, INV-OBS-004, INV-OBS-005, INV-OBS-006, INV-OBS-007
- **Canonical References:** DecisionReference, ExecutionReference, KnowledgeAssetReference, PolicyReference
- **Derived From:** OES-005 / Observability Domain

##### Behavioral Projection

- **Category:** Lifecycle
- **Purpose:** Archive audit evidence.
- **Business Meaning:** Provides the institutional behavior required to satisfy the OES-005 capability `ArchiveEvidence` for `AuditRecord`.
- **Required Inputs:** AuditRecord Retained
- **Optional Inputs:** none unless allowed by the governing policy.
- **Produced Objects:** AuditRecord Archived
- **Produced References:** AuditRecordReference
- **Preconditions:** `AuditRecord` must be available and the applicable policy/authority `Retention Policy` must be resolved.
- **Postconditions:** Evidence remains retrievable by policy.
- **Failure Conditions:** Reject when required inputs are missing, policy/authority cannot be resolved, referenced concepts are unavailable, or related invariants would be violated.
- **Primary Contract:** CON-OBS-005 — ArchiveEvidenceCommand
- **Primary Event:** EVT-OBS-005 — AuditRecordArchived
- **Runtime Projection:** RUN-OBS-005 ArchiveEvidenceRuntimeProjection
- **Traceability:** OES-005::Observability Domain::CAP-OBS-005
- **Verification Status:** VERIFIED

## Cross-Cutting Rules

- OES-006 shall not introduce new capabilities outside the 56 capabilities declared in OES-005.
- OES-006 shall not rename or reuse capability IDs.
- OES-006 shall not change aggregate ownership, authority, lifecycle, invariants or references inherited from OES-005.
- Each capability shall define exactly one primary contract and one primary event for downstream derivation.
- Runtime projections are declarative and do not prescribe implementation technology.

## Traceability Matrix

| Capability ID | Capability Name | Aggregate Root | Contract | Event | Runtime Projection |
|---|---|---|---|---|---|
| CAP-IDN-001 | CreateOrganization | DOM-001 Organization | CON-IDN-001 | EVT-IDN-001 | RUN-IDN-001 |
| CAP-IDN-002 | ActivateOrganization | DOM-001 Organization | CON-IDN-002 | EVT-IDN-002 | RUN-IDN-002 |
| CAP-IDN-003 | SuspendOrganization | DOM-001 Organization | CON-IDN-003 | EVT-IDN-003 | RUN-IDN-003 |
| CAP-IDN-004 | ArchiveOrganization | DOM-001 Organization | CON-IDN-004 | EVT-IDN-004 | RUN-IDN-004 |
| CAP-IDN-005 | CreateWorkspace | DOM-001 Organization | CON-IDN-005 | EVT-IDN-005 | RUN-IDN-005 |
| CAP-IDN-006 | InviteMember | DOM-001 Organization | CON-IDN-006 | EVT-IDN-006 | RUN-IDN-006 |
| CAP-IDN-007 | ActivateMembership | DOM-001 Organization | CON-IDN-007 | EVT-IDN-007 | RUN-IDN-007 |
| CAP-IDN-008 | SuspendMembership | DOM-001 Organization | CON-IDN-008 | EVT-IDN-008 | RUN-IDN-008 |
| CAP-IDN-009 | RevokeMembership | DOM-001 Organization | CON-IDN-009 | EVT-IDN-009 | RUN-IDN-009 |
| CAP-KNW-001 | CreateKnowledgeAsset | DOM-010 KnowledgeAsset | CON-KNW-001 | EVT-KNW-001 | RUN-KNW-001 |
| CAP-KNW-002 | ValidateKnowledgeAsset | DOM-010 KnowledgeAsset | CON-KNW-002 | EVT-KNW-002 | RUN-KNW-002 |
| CAP-KNW-003 | ApproveKnowledgeAsset | DOM-010 KnowledgeAsset | CON-KNW-003 | EVT-KNW-003 | RUN-KNW-003 |
| CAP-KNW-004 | OperationalizeKnowledgeAsset | DOM-010 KnowledgeAsset | CON-KNW-004 | EVT-KNW-004 | RUN-KNW-004 |
| CAP-KNW-005 | ArchiveKnowledgeAsset | DOM-010 KnowledgeAsset | CON-KNW-005 | EVT-KNW-005 | RUN-KNW-005 |
| CAP-AGT-001 | CreateAgent | DOM-020 Agent | CON-AGT-001 | EVT-AGT-001 | RUN-AGT-001 |
| CAP-AGT-002 | ApproveAgent | DOM-020 Agent | CON-AGT-002 | EVT-AGT-002 | RUN-AGT-002 |
| CAP-AGT-003 | BindCapability | DOM-020 Agent | CON-AGT-003 | EVT-AGT-003 | RUN-AGT-003 |
| CAP-AGT-004 | ActivateAgent | DOM-020 Agent | CON-AGT-004 | EVT-AGT-004 | RUN-AGT-004 |
| CAP-AGT-005 | SuspendAgent | DOM-020 Agent | CON-AGT-005 | EVT-AGT-005 | RUN-AGT-005 |
| CAP-AGT-006 | ArchiveAgent | DOM-020 Agent | CON-AGT-006 | EVT-AGT-006 | RUN-AGT-006 |
| CAP-CON-001 | OpenConversation | DOM-030 Conversation | CON-CON-001 | EVT-CON-001 | RUN-CON-001 |
| CAP-CON-002 | AppendMessage | DOM-030 Conversation | CON-CON-002 | EVT-CON-002 | RUN-CON-002 |
| CAP-CON-003 | ResolveContext | DOM-030 Conversation | CON-CON-003 | EVT-CON-003 | RUN-CON-003 |
| CAP-CON-004 | PauseConversation | DOM-030 Conversation | CON-CON-004 | EVT-CON-004 | RUN-CON-004 |
| CAP-CON-005 | ResumeConversation | DOM-030 Conversation | CON-CON-005 | EVT-CON-005 | RUN-CON-005 |
| CAP-CON-006 | CloseConversation | DOM-030 Conversation | CON-CON-006 | EVT-CON-006 | RUN-CON-006 |
| CAP-CON-007 | ArchiveConversation | DOM-030 Conversation | CON-CON-007 | EVT-CON-007 | RUN-CON-007 |
| CAP-DEC-001 | CreateDecision | DOM-040 Decision | CON-DEC-001 | EVT-DEC-001 | RUN-DEC-001 |
| CAP-DEC-002 | AttachEvidence | DOM-040 Decision | CON-DEC-002 | EVT-DEC-002 | RUN-DEC-002 |
| CAP-DEC-003 | SubmitDecisionReview | DOM-040 Decision | CON-DEC-003 | EVT-DEC-003 | RUN-DEC-003 |
| CAP-DEC-004 | ApproveDecision | DOM-040 Decision | CON-DEC-004 | EVT-DEC-004 | RUN-DEC-004 |
| CAP-DEC-005 | RejectDecision | DOM-040 Decision | CON-DEC-005 | EVT-DEC-005 | RUN-DEC-005 |
| CAP-DEC-006 | PublishDecision | DOM-040 Decision | CON-DEC-006 | EVT-DEC-006 | RUN-DEC-006 |
| CAP-DEC-007 | SupersedeDecision | DOM-040 Decision | CON-DEC-007 | EVT-DEC-007 | RUN-DEC-007 |
| CAP-DEC-008 | ArchiveDecision | DOM-040 Decision | CON-DEC-008 | EVT-DEC-008 | RUN-DEC-008 |
| CAP-EXE-001 | PlanExecution | DOM-050 Execution | CON-EXE-001 | EVT-EXE-001 | RUN-EXE-001 |
| CAP-EXE-002 | AuthorizeExecution | DOM-050 Execution | CON-EXE-002 | EVT-EXE-002 | RUN-EXE-002 |
| CAP-EXE-003 | StartExecution | DOM-050 Execution | CON-EXE-003 | EVT-EXE-003 | RUN-EXE-003 |
| CAP-EXE-004 | CompleteExecution | DOM-050 Execution | CON-EXE-004 | EVT-EXE-004 | RUN-EXE-004 |
| CAP-EXE-005 | VerifyExecution | DOM-050 Execution | CON-EXE-005 | EVT-EXE-005 | RUN-EXE-005 |
| CAP-EXE-006 | ArchiveExecution | DOM-050 Execution | CON-EXE-006 | EVT-EXE-006 | RUN-EXE-006 |
| CAP-EXE-007 | PromoteArtifactToKnowledge | DOM-050 Execution | CON-EXE-007 | EVT-EXE-007 | RUN-EXE-007 |
| CAP-GOV-001 | CreatePolicy | DOM-060 Policy | CON-GOV-001 | EVT-GOV-001 | RUN-GOV-001 |
| CAP-GOV-002 | SubmitPolicyReview | DOM-060 Policy | CON-GOV-002 | EVT-GOV-002 | RUN-GOV-002 |
| CAP-GOV-003 | ApprovePolicy | DOM-060 Policy | CON-GOV-003 | EVT-GOV-003 | RUN-GOV-003 |
| CAP-GOV-004 | RejectPolicy | DOM-060 Policy | CON-GOV-004 | EVT-GOV-004 | RUN-GOV-004 |
| CAP-GOV-005 | PublishPolicy | DOM-060 Policy | CON-GOV-005 | EVT-GOV-005 | RUN-GOV-005 |
| CAP-GOV-006 | SupersedePolicy | DOM-060 Policy | CON-GOV-006 | EVT-GOV-006 | RUN-GOV-006 |
| CAP-GOV-007 | DelegateAuthority | DOM-060 Policy | CON-GOV-007 | EVT-GOV-007 | RUN-GOV-007 |
| CAP-GOV-008 | RevokeDelegation | DOM-060 Policy | CON-GOV-008 | EVT-GOV-008 | RUN-GOV-008 |
| CAP-GOV-009 | ArchivePolicy | DOM-060 Policy | CON-GOV-009 | EVT-GOV-009 | RUN-GOV-009 |
| CAP-OBS-001 | RegisterAuditRecord | DOM-070 AuditRecord | CON-OBS-001 | EVT-OBS-001 | RUN-OBS-001 |
| CAP-OBS-002 | ValidateEvidence | DOM-070 AuditRecord | CON-OBS-002 | EVT-OBS-002 | RUN-OBS-002 |
| CAP-OBS-003 | CorrelateEvidence | DOM-070 AuditRecord | CON-OBS-003 | EVT-OBS-003 | RUN-OBS-003 |
| CAP-OBS-004 | ApplyRetentionPolicy | DOM-070 AuditRecord | CON-OBS-004 | EVT-OBS-004 | RUN-OBS-004 |
| CAP-OBS-005 | ArchiveEvidence | DOM-070 AuditRecord | CON-OBS-005 | EVT-OBS-005 | RUN-OBS-005 |

## Acceptance Criteria

- 56 expected capabilities are present.
- No expected capability is missing.
- No extra capability exists.
- No capability ID is renamed or reused.
- All inherited canonical fields match OES-005.
- All behavioral projection fields are populated.
- Coverage check returns PASS.
- Package hygiene check returns PASS.
- Produced References resolve only to the canonical reference inventory.

## Derivation Compliance

This document was reconstructed from OES-005 / OES-RC-0002-R4. The supporting package includes a Canonical Capability Set and Baseline Fidelity Report to make this derivation auditable.

## Revision History

| Version | Status | Description |
|---|---|---|
| 0.1-rc | Rejected | Initial RC diverged from OES-005/R4 and was not promoted. |
| 0.1-rc-r2 | Release Candidate | Deterministic reconstruction from OES-005/R4 with 56/56 capability fidelity. |
| 0.1-rc-r3 | Release Candidate | Vocabulary closure, Produced References validator hardening, replacement policy alignment and editorial cleanup. |