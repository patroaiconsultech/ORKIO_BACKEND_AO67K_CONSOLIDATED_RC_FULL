# OES-RC-0004-R1 — Contract Event Projection Matrix

| Domain | Capability | Contract | Event | Required Inputs | Produced Objects | Produced References |
|---|---|---|---|---|---|---|
| Identity Domain | `CAP-IDN-001` CreateOrganization | `CON-IDN-001` CreateOrganizationCommand | `EVT-IDN-001` OrganizationCreated | Organization profile | Organization Draft | OrganizationReference |
| Identity Domain | `CAP-IDN-002` ActivateOrganization | `CON-IDN-002` ActivateOrganizationCommand | `EVT-IDN-002` OrganizationActivated | Organization Draft | Organization Active | OrganizationReference |
| Identity Domain | `CAP-IDN-003` SuspendOrganization | `CON-IDN-003` SuspendOrganizationCommand | `EVT-IDN-003` OrganizationSuspended | Organization Active | Organization Suspended | OrganizationReference |
| Identity Domain | `CAP-IDN-004` ArchiveOrganization | `CON-IDN-004` ArchiveOrganizationCommand | `EVT-IDN-004` OrganizationArchived | Organization terminal | Organization Archived | OrganizationReference |
| Identity Domain | `CAP-IDN-005` CreateWorkspace | `CON-IDN-005` CreateWorkspaceCommand | `EVT-IDN-005` WorkspaceCreated | Organization, workspace profile | Workspace | WorkspaceReference |
| Identity Domain | `CAP-IDN-006` InviteMember | `CON-IDN-006` InviteMemberCommand | `EVT-IDN-006` MemberInvited | Person, Organization/Workspace | Membership Pending | OrganizationReference |
| Identity Domain | `CAP-IDN-007` ActivateMembership | `CON-IDN-007` ActivateMembershipCommand | `EVT-IDN-007` MembershipActivated | Membership Pending | Membership Active | OrganizationReference |
| Identity Domain | `CAP-IDN-008` SuspendMembership | `CON-IDN-008` SuspendMembershipCommand | `EVT-IDN-008` MembershipSuspended | Membership Active | Membership Suspended | OrganizationReference |
| Identity Domain | `CAP-IDN-009` RevokeMembership | `CON-IDN-009` RevokeMembershipCommand | `EVT-IDN-009` MembershipRevoked | Membership Active/Suspended | Membership Revoked | OrganizationReference |
| Knowledge Domain | `CAP-KNW-001` CreateKnowledgeAsset | `CON-KNW-001` CreateKnowledgeAssetCommand | `EVT-KNW-001` KnowledgeAssetCreated | Source, classification, content reference | KnowledgeAsset Draft | KnowledgeAssetReference |
| Knowledge Domain | `CAP-KNW-002` ValidateKnowledgeAsset | `CON-KNW-002` ValidateKnowledgeAssetCommand | `EVT-KNW-002` KnowledgeAssetValidated | KnowledgeAsset Draft | KnowledgeAsset Validated | KnowledgeAssetReference |
| Knowledge Domain | `CAP-KNW-003` ApproveKnowledgeAsset | `CON-KNW-003` ApproveKnowledgeAssetCommand | `EVT-KNW-003` KnowledgeAssetApproved | KnowledgeAsset Validated | KnowledgeAsset Approved | KnowledgeAssetReference |
| Knowledge Domain | `CAP-KNW-004` OperationalizeKnowledgeAsset | `CON-KNW-004` OperationalizeKnowledgeAssetCommand | `EVT-KNW-004` KnowledgeAssetOperationalized | KnowledgeAsset Approved | KnowledgeAsset Operational | KnowledgeAssetReference |
| Knowledge Domain | `CAP-KNW-005` ArchiveKnowledgeAsset | `CON-KNW-005` ArchiveKnowledgeAssetCommand | `EVT-KNW-005` KnowledgeAssetArchived | KnowledgeAsset | KnowledgeAsset Archived | KnowledgeAssetReference |
| Agent Domain | `CAP-AGT-001` CreateAgent | `CON-AGT-001` CreateAgentCommand | `EVT-AGT-001` AgentCreated | AgentProfile | Agent Draft | AgentReference |
| Agent Domain | `CAP-AGT-002` ApproveAgent | `CON-AGT-002` ApproveAgentCommand | `EVT-AGT-002` AgentApproved | Agent Draft | Agent Approved | AgentReference |
| Agent Domain | `CAP-AGT-003` BindCapability | `CON-AGT-003` BindCapabilityCommand | `EVT-AGT-003` CapabilityBound | Agent, Capability | CapabilityBinding | AgentReference |
| Agent Domain | `CAP-AGT-004` ActivateAgent | `CON-AGT-004` ActivateAgentCommand | `EVT-AGT-004` AgentActivated | Agent Approved | Agent Active | AgentReference |
| Agent Domain | `CAP-AGT-005` SuspendAgent | `CON-AGT-005` SuspendAgentCommand | `EVT-AGT-005` AgentSuspended | Agent Active | Agent Suspended | AgentReference |
| Agent Domain | `CAP-AGT-006` ArchiveAgent | `CON-AGT-006` ArchiveAgentCommand | `EVT-AGT-006` AgentArchived | Agent Suspended/Approved | Agent Archived | AgentReference |
| Conversation Domain | `CAP-CON-001` OpenConversation | `CON-CON-001` OpenConversationCommand | `EVT-CON-001` ConversationCreated | Workspace, participant | Conversation Created | ConversationReference |
| Conversation Domain | `CAP-CON-002` AppendMessage | `CON-CON-002` AppendMessageCommand | `EVT-CON-002` MessageRecorded | Conversation, message | Message / Conversation Active | ConversationReference |
| Conversation Domain | `CAP-CON-003` ResolveContext | `CON-CON-003` ResolveContextCommand | `EVT-CON-003` ContextResolved | Conversation | ContextSnapshot | ConversationReference |
| Conversation Domain | `CAP-CON-004` PauseConversation | `CON-CON-004` PauseConversationCommand | `EVT-CON-004` ConversationPaused | Conversation Active | Conversation Paused | ConversationReference |
| Conversation Domain | `CAP-CON-005` ResumeConversation | `CON-CON-005` ResumeConversationCommand | `EVT-CON-005` ConversationResumed | Conversation Paused | Conversation Active | ConversationReference |
| Conversation Domain | `CAP-CON-006` CloseConversation | `CON-CON-006` CloseConversationCommand | `EVT-CON-006` ConversationClosed | Conversation Active/Paused | Conversation Closed | ConversationReference |
| Conversation Domain | `CAP-CON-007` ArchiveConversation | `CON-CON-007` ArchiveConversationCommand | `EVT-CON-007` ConversationArchived | Conversation Closed | Conversation Archived | ConversationReference |
| Decision Domain | `CAP-DEC-001` CreateDecision | `CON-DEC-001` CreateDecisionCommand | `EVT-DEC-001` DecisionCreated | Context, rationale draft | Decision Draft | DecisionReference |
| Decision Domain | `CAP-DEC-002` AttachEvidence | `CON-DEC-002` AttachEvidenceCommand | `EVT-DEC-002` EvidenceAttached | Decision, EvidenceReference | Decision with Evidence | EvidenceReference |
| Decision Domain | `CAP-DEC-003` SubmitDecisionReview | `CON-DEC-003` SubmitDecisionReviewCommand | `EVT-DEC-003` DecisionSubmitted | Decision Draft | Decision Under Review | DecisionReference |
| Decision Domain | `CAP-DEC-004` ApproveDecision | `CON-DEC-004` ApproveDecisionCommand | `EVT-DEC-004` DecisionApproved | Decision Under Review | Decision Approved | DecisionReference |
| Decision Domain | `CAP-DEC-005` RejectDecision | `CON-DEC-005` RejectDecisionCommand | `EVT-DEC-005` DecisionRejected | Decision Under Review | Decision Rejected | DecisionReference |
| Decision Domain | `CAP-DEC-006` PublishDecision | `CON-DEC-006` PublishDecisionCommand | `EVT-DEC-006` DecisionPublished | Decision Approved | Decision Effective | DecisionReference |
| Decision Domain | `CAP-DEC-007` SupersedeDecision | `CON-DEC-007` SupersedeDecisionCommand | `EVT-DEC-007` DecisionSuperseded | Decision Effective, new Decision | Decision Superseded | DecisionReference |
| Decision Domain | `CAP-DEC-008` ArchiveDecision | `CON-DEC-008` ArchiveDecisionCommand | `EVT-DEC-008` DecisionArchived | Decision terminal | Decision Archived | DecisionReference |
| Execution Domain | `CAP-EXE-001` PlanExecution | `CON-EXE-001` PlanExecutionCommand | `EVT-EXE-001` ExecutionPlanned | Decision/Policy | Execution Planned | ExecutionReference |
| Execution Domain | `CAP-EXE-002` AuthorizeExecution | `CON-EXE-002` AuthorizeExecutionCommand | `EVT-EXE-002` ExecutionAuthorized | Execution Planned | Execution Authorized | ExecutionReference |
| Execution Domain | `CAP-EXE-003` StartExecution | `CON-EXE-003` StartExecutionCommand | `EVT-EXE-003` ExecutionStarted | Execution Authorized | Execution Running | ExecutionReference |
| Execution Domain | `CAP-EXE-004` CompleteExecution | `CON-EXE-004` CompleteExecutionCommand | `EVT-EXE-004` ExecutionCompleted | Execution Running | Execution Completed | ExecutionReference |
| Execution Domain | `CAP-EXE-005` VerifyExecution | `CON-EXE-005` VerifyExecutionCommand | `EVT-EXE-005` ExecutionVerified | Execution Completed | Execution Verified | ExecutionReference |
| Execution Domain | `CAP-EXE-006` ArchiveExecution | `CON-EXE-006` ArchiveExecutionCommand | `EVT-EXE-006` ExecutionArchived | Execution Verified | Execution Archived | ExecutionReference |
| Execution Domain | `CAP-EXE-007` PromoteArtifactToKnowledge | `CON-EXE-007` PromoteArtifactToKnowledgeCommand | `EVT-EXE-007` ExecutionArtifactProduced | Artifact, provenance | KnowledgeAsset Draft | KnowledgeAssetReference |
| Governance Domain | `CAP-GOV-001` CreatePolicy | `CON-GOV-001` CreatePolicyCommand | `EVT-GOV-001` PolicyCreated | Scope, rules draft | Policy Draft | PolicyReference |
| Governance Domain | `CAP-GOV-002` SubmitPolicyReview | `CON-GOV-002` SubmitPolicyReviewCommand | `EVT-GOV-002` PolicySubmitted | Policy Draft | Policy Under Review | PolicyReference |
| Governance Domain | `CAP-GOV-003` ApprovePolicy | `CON-GOV-003` ApprovePolicyCommand | `EVT-GOV-003` PolicyApproved | Policy Under Review | Policy Approved | PolicyReference |
| Governance Domain | `CAP-GOV-004` RejectPolicy | `CON-GOV-004` RejectPolicyCommand | `EVT-GOV-004` PolicyRejected | Policy Under Review | Policy Rejected | PolicyReference |
| Governance Domain | `CAP-GOV-005` PublishPolicy | `CON-GOV-005` PublishPolicyCommand | `EVT-GOV-005` PolicyPublished | Policy Approved | Policy Effective | PolicyReference |
| Governance Domain | `CAP-GOV-006` SupersedePolicy | `CON-GOV-006` SupersedePolicyCommand | `EVT-GOV-006` PolicySuperseded | Policy Effective, new Policy | Policy Superseded | PolicyReference |
| Governance Domain | `CAP-GOV-007` DelegateAuthority | `CON-GOV-007` DelegateAuthorityCommand | `EVT-GOV-007` DelegationGranted | Authority, delegate, scope | Delegation | PolicyReference |
| Governance Domain | `CAP-GOV-008` RevokeDelegation | `CON-GOV-008` RevokeDelegationCommand | `EVT-GOV-008` DelegationRevoked | Delegation | Delegation Revoked | PolicyReference |
| Governance Domain | `CAP-GOV-009` ArchivePolicy | `CON-GOV-009` ArchivePolicyCommand | `EVT-GOV-009` PolicyArchived | Policy terminal | Policy Archived | PolicyReference |
| Observability Domain | `CAP-OBS-001` RegisterAuditRecord | `CON-OBS-001` RegisterAuditRecordCommand | `EVT-OBS-001` AuditRecordRegistered | Context, evidence | AuditRecord Registered | AuditRecordReference |
| Observability Domain | `CAP-OBS-002` ValidateEvidence | `CON-OBS-002` ValidateEvidenceCommand | `EVT-OBS-002` EvidenceValidated | AuditRecord | AuditRecord Validated | AuditRecordReference |
| Observability Domain | `CAP-OBS-003` CorrelateEvidence | `CON-OBS-003` CorrelateEvidenceCommand | `EVT-OBS-003` EvidenceCorrelated | AuditRecords | Correlation | AuditRecordReference |
| Observability Domain | `CAP-OBS-004` ApplyRetentionPolicy | `CON-OBS-004` ApplyRetentionPolicyCommand | `EVT-OBS-004` RetentionApplied | AuditRecord | AuditRecord Retained | AuditRecordReference |
| Observability Domain | `CAP-OBS-005` ArchiveEvidence | `CON-OBS-005` ArchiveEvidenceCommand | `EVT-OBS-005` AuditRecordArchived | AuditRecord Retained | AuditRecord Archived | AuditRecordReference |
