# CAPABILITY_TRANSITION_MATRIX

| Capability ID | Capability Name | Input State/Object | Output State/Object | Lifecycle Source |
|---|---|---|---|---|
| CAP-IDN-001 | CreateOrganization | Organization profile | Organization Draft | Organization has `Draft → Active → Suspended → Archived` |
| CAP-IDN-002 | ActivateOrganization | Organization Draft | Organization Active | Organization has `Draft → Active → Suspended → Archived` |
| CAP-IDN-003 | SuspendOrganization | Organization Active | Organization Suspended | Organization has `Draft → Active → Suspended → Archived` |
| CAP-IDN-004 | ArchiveOrganization | Organization terminal | Organization Archived | Organization has `Draft → Active → Suspended → Archived` |
| CAP-IDN-005 | CreateWorkspace | Organization, workspace profile | Workspace | Organization has `Draft → Active → Suspended → Archived` |
| CAP-IDN-006 | InviteMember | Person, Organization/Workspace | Membership Pending | Organization has `Draft → Active → Suspended → Archived` |
| CAP-IDN-007 | ActivateMembership | Membership Pending | Membership Active | Organization has `Draft → Active → Suspended → Archived` |
| CAP-IDN-008 | SuspendMembership | Membership Active | Membership Suspended | Organization has `Draft → Active → Suspended → Archived` |
| CAP-IDN-009 | RevokeMembership | Membership Active/Suspended | Membership Revoked | Organization has `Draft → Active → Suspended → Archived` |
| CAP-KNW-001 | CreateKnowledgeAsset | Source, classification, content reference | KnowledgeAsset Draft | `Draft → Validated → Approved → Operational → Archived` |
| CAP-KNW-002 | ValidateKnowledgeAsset | KnowledgeAsset Draft | KnowledgeAsset Validated | `Draft → Validated → Approved → Operational → Archived` |
| CAP-KNW-003 | ApproveKnowledgeAsset | KnowledgeAsset Validated | KnowledgeAsset Approved | `Draft → Validated → Approved → Operational → Archived` |
| CAP-KNW-004 | OperationalizeKnowledgeAsset | KnowledgeAsset Approved | KnowledgeAsset Operational | `Draft → Validated → Approved → Operational → Archived` |
| CAP-KNW-005 | ArchiveKnowledgeAsset | KnowledgeAsset | KnowledgeAsset Archived | `Draft → Validated → Approved → Operational → Archived` |
| CAP-AGT-001 | CreateAgent | AgentProfile | Agent Draft | `Draft → Approved → Active → Suspended → Archived` |
| CAP-AGT-002 | ApproveAgent | Agent Draft | Agent Approved | `Draft → Approved → Active → Suspended → Archived` |
| CAP-AGT-003 | BindCapability | Agent, Capability | CapabilityBinding | `Draft → Approved → Active → Suspended → Archived` |
| CAP-AGT-004 | ActivateAgent | Agent Approved | Agent Active | `Draft → Approved → Active → Suspended → Archived` |
| CAP-AGT-005 | SuspendAgent | Agent Active | Agent Suspended | `Draft → Approved → Active → Suspended → Archived` |
| CAP-AGT-006 | ArchiveAgent | Agent Suspended/Approved | Agent Archived | `Draft → Approved → Active → Suspended → Archived` |
| CAP-CON-001 | OpenConversation | Workspace, participant | Conversation Created | `Created → Active → Paused → Active → Closed → Archived` |
| CAP-CON-002 | AppendMessage | Conversation, message | Message / Conversation Active | `Created → Active → Paused → Active → Closed → Archived` |
| CAP-CON-003 | ResolveContext | Conversation | ContextSnapshot | `Created → Active → Paused → Active → Closed → Archived` |
| CAP-CON-004 | PauseConversation | Conversation Active | Conversation Paused | `Created → Active → Paused → Active → Closed → Archived` |
| CAP-CON-005 | ResumeConversation | Conversation Paused | Conversation Active | `Created → Active → Paused → Active → Closed → Archived` |
| CAP-CON-006 | CloseConversation | Conversation Active/Paused | Conversation Closed | `Created → Active → Paused → Active → Closed → Archived` |
| CAP-CON-007 | ArchiveConversation | Conversation Closed | Conversation Archived | `Created → Active → Paused → Active → Closed → Archived` |
| CAP-DEC-001 | CreateDecision | Context, rationale draft | Decision Draft | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-DEC-002 | AttachEvidence | Decision, EvidenceReference | Decision with Evidence | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-DEC-003 | SubmitDecisionReview | Decision Draft | Decision Under Review | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-DEC-004 | ApproveDecision | Decision Under Review | Decision Approved | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-DEC-005 | RejectDecision | Decision Under Review | Decision Rejected | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-DEC-006 | PublishDecision | Decision Approved | Decision Effective | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-DEC-007 | SupersedeDecision | Decision Effective, new Decision | Decision Superseded | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-DEC-008 | ArchiveDecision | Decision terminal | Decision Archived | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-EXE-001 | PlanExecution | Decision/Policy | Execution Planned | `Planned → Authorized → Running → Completed → Verified → Archived` |
| CAP-EXE-002 | AuthorizeExecution | Execution Planned | Execution Authorized | `Planned → Authorized → Running → Completed → Verified → Archived` |
| CAP-EXE-003 | StartExecution | Execution Authorized | Execution Running | `Planned → Authorized → Running → Completed → Verified → Archived` |
| CAP-EXE-004 | CompleteExecution | Execution Running | Execution Completed | `Planned → Authorized → Running → Completed → Verified → Archived` |
| CAP-EXE-005 | VerifyExecution | Execution Completed | Execution Verified | `Planned → Authorized → Running → Completed → Verified → Archived` |
| CAP-EXE-006 | ArchiveExecution | Execution Verified | Execution Archived | `Planned → Authorized → Running → Completed → Verified → Archived` |
| CAP-EXE-007 | PromoteArtifactToKnowledge | Artifact, provenance | KnowledgeAsset Draft | `Planned → Authorized → Running → Completed → Verified → Archived` |
| CAP-GOV-001 | CreatePolicy | Scope, rules draft | Policy Draft | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-GOV-002 | SubmitPolicyReview | Policy Draft | Policy Under Review | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-GOV-003 | ApprovePolicy | Policy Under Review | Policy Approved | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-GOV-004 | RejectPolicy | Policy Under Review | Policy Rejected | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-GOV-005 | PublishPolicy | Policy Approved | Policy Effective | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-GOV-006 | SupersedePolicy | Policy Effective, new Policy | Policy Superseded | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-GOV-007 | DelegateAuthority | Authority, delegate, scope | Delegation | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-GOV-008 | RevokeDelegation | Delegation | Delegation Revoked | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-GOV-009 | ArchivePolicy | Policy terminal | Policy Archived | `Draft → Under Review → Rejected → Archived` or `Draft → Under Review → Approved → Effective → Superseded → Archived` |
| CAP-OBS-001 | RegisterAuditRecord | Context, evidence | AuditRecord Registered | `Registered → Validated → Retained → Archived` |
| CAP-OBS-002 | ValidateEvidence | AuditRecord | AuditRecord Validated | `Registered → Validated → Retained → Archived` |
| CAP-OBS-003 | CorrelateEvidence | AuditRecords | Correlation | `Registered → Validated → Retained → Archived` |
| CAP-OBS-004 | ApplyRetentionPolicy | AuditRecord | AuditRecord Retained | `Registered → Validated → Retained → Archived` |
| CAP-OBS-005 | ArchiveEvidence | AuditRecord Retained | AuditRecord Archived | `Registered → Validated → Retained → Archived` |