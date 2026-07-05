# Derivation Matrix

This matrix is normative and complete for state-changing capabilities in OES-RC-0002-R4.

| Aggregate | Capability | Contract | State Transition | Event | Runtime Derivation |
|---|---|---|---|---|---|
| Organization | CreateOrganization | CreateOrganization | none → Draft | OrganizationCreated | Lifecycle transition owned by Governance Authority. |
| Organization | ActivateOrganization | ActivateOrganization | Draft → Active | OrganizationActivated | Lifecycle transition owned by Governance Authority. |
| Organization | SuspendOrganization | SuspendOrganization | Active → Suspended | OrganizationSuspended | Lifecycle transition owned by Governance Authority. |
| Organization | ArchiveOrganization | ArchiveOrganization | Active/Suspended → Archived | OrganizationArchived | Lifecycle transition owned by Governance Authority. |
| Membership | InviteMember | InviteMember | none → Pending | MemberInvited | Lifecycle transition owned by Governance Authority. |
| Membership | ActivateMembership | ActivateMembership | Pending → Active | MembershipActivated | Lifecycle transition owned by Governance Authority. |
| Membership | SuspendMembership | SuspendMembership | Active → Suspended | MembershipSuspended | Lifecycle transition owned by Governance Authority. |
| Membership | RevokeMembership | RevokeMembership | Active/Suspended → Revoked | MembershipRevoked | Lifecycle transition owned by Governance Authority. |
| KnowledgeAsset | CreateKnowledgeAsset | CreateKnowledgeAsset | none → Draft | KnowledgeAssetCreated | Lifecycle transition owned by Knowledge Authority. |
| KnowledgeAsset | ValidateKnowledgeAsset | ValidateKnowledgeAsset | Draft → Validated | KnowledgeAssetValidated | Lifecycle transition owned by Knowledge Authority. |
| KnowledgeAsset | ApproveKnowledgeAsset | ApproveKnowledgeAsset | Validated → Approved | KnowledgeAssetApproved | Lifecycle transition owned by Knowledge Authority. |
| KnowledgeAsset | OperationalizeKnowledgeAsset | OperationalizeKnowledgeAsset | Approved → Operational | KnowledgeAssetOperationalized | Lifecycle transition owned by Knowledge Authority. |
| KnowledgeAsset | ArchiveKnowledgeAsset | ArchiveKnowledgeAsset | Any non-Archived → Archived | KnowledgeAssetArchived | Lifecycle transition owned by Knowledge Authority. |
| Agent | CreateAgent | CreateAgent | none → Draft | AgentCreated | Lifecycle transition owned by Capability Authority. |
| Agent | ApproveAgent | ApproveAgent | Draft → Approved | AgentApproved | Lifecycle transition owned by Capability Authority. |
| Agent | ActivateAgent | ActivateAgent | Approved → Active | AgentActivated | Lifecycle transition owned by Capability Authority. |
| Agent | SuspendAgent | SuspendAgent | Active → Suspended | AgentSuspended | Lifecycle transition owned by Capability Authority. |
| Agent | ArchiveAgent | ArchiveAgent | Approved/Suspended → Archived | AgentArchived | Lifecycle transition owned by Capability Authority. |
| Conversation | OpenConversation | OpenConversation | none → Created | ConversationCreated | Lifecycle transition owned by Runtime Authority. |
| Conversation | AppendMessage | AppendMessage | Created/Active → Active | MessageRecorded | Lifecycle transition owned by Runtime Authority. |
| Conversation | PauseConversation | PauseConversation | Active → Paused | ConversationPaused | Lifecycle transition owned by Runtime Authority. |
| Conversation | ResumeConversation | ResumeConversation | Paused → Active | ConversationResumed | Lifecycle transition owned by Runtime Authority. |
| Conversation | CloseConversation | CloseConversation | Active/Paused → Closed | ConversationClosed | Lifecycle transition owned by Runtime Authority. |
| Conversation | ArchiveConversation | ArchiveConversation | Closed → Archived | ConversationArchived | Lifecycle transition owned by Runtime Authority. |
| Decision | CreateDecision | CreateDecision | none → Draft | DecisionCreated | Lifecycle transition owned by Decision Authority. |
| Decision | AttachEvidence | AttachEvidence | Draft → Draft | EvidenceAttached | Lifecycle transition owned by Decision Authority. |
| Decision | SubmitDecisionReview | SubmitDecisionReview | Draft → Under Review | DecisionSubmitted | Lifecycle transition owned by Decision Authority. |
| Decision | ApproveDecision | ApproveDecision | Under Review → Approved | DecisionApproved | Lifecycle transition owned by Decision Authority. |
| Decision | RejectDecision | RejectDecision | Under Review → Rejected | DecisionRejected | Lifecycle transition owned by Decision Authority. |
| Decision | PublishDecision | PublishDecision | Approved → Effective | DecisionPublished | Lifecycle transition owned by Decision Authority. |
| Decision | SupersedeDecision | SupersedeDecision | Effective → Superseded | DecisionSuperseded | Lifecycle transition owned by Decision Authority. |
| Decision | ArchiveDecision | ArchiveDecision | Rejected/Effective/Superseded → Archived | DecisionArchived | Lifecycle transition owned by Decision Authority. |
| Execution | PlanExecution | PlanExecution | none → Planned | ExecutionPlanned | Lifecycle transition owned by Runtime Authority. |
| Execution | AuthorizeExecution | AuthorizeExecution | Planned → Authorized | ExecutionAuthorized | Lifecycle transition owned by Runtime Authority. |
| Execution | StartExecution | StartExecution | Authorized → Running | ExecutionStarted | Lifecycle transition owned by Runtime Authority. |
| Execution | CompleteExecution | CompleteExecution | Running → Completed | ExecutionCompleted | Lifecycle transition owned by Runtime Authority. |
| Execution | VerifyExecution | VerifyExecution | Completed → Verified | ExecutionVerified | Lifecycle transition owned by Runtime Authority. |
| Execution | ArchiveExecution | ArchiveExecution | Verified → Archived | ExecutionArchived | Lifecycle transition owned by Runtime Authority. |
| Execution | PromoteArtifactToKnowledge | PromoteArtifactToKnowledge | Completed/Verified → KnowledgeAsset Draft | ArtifactPromotionRequested / KnowledgeAssetCreated | Lifecycle transition owned by Knowledge Authority. |
| Policy | CreatePolicy | CreatePolicy | none → Draft | PolicyCreated | Lifecycle transition owned by Governance Authority. |
| Policy | SubmitPolicyReview | SubmitPolicyReview | Draft → Under Review | PolicySubmitted | Lifecycle transition owned by Governance Authority. |
| Policy | ApprovePolicy | ApprovePolicy | Under Review → Approved | PolicyApproved | Lifecycle transition owned by Governance Authority. |
| Policy | RejectPolicy | RejectPolicy | Under Review → Rejected | PolicyRejected | Lifecycle transition owned by Governance Authority. |
| Policy | PublishPolicy | PublishPolicy | Approved → Effective | PolicyPublished | Lifecycle transition owned by Governance Authority. |
| Policy | SupersedePolicy | SupersedePolicy | Effective → Superseded | PolicySuperseded | Lifecycle transition owned by Governance Authority. |
| Policy | ArchivePolicy | ArchivePolicy | Rejected/Effective/Superseded → Archived | PolicyArchived | Lifecycle transition owned by Governance Authority. |
| Delegation | RevokeDelegation | RevokeDelegation | Active → Revoked | DelegationRevoked | Lifecycle transition owned by Governance Authority. |
| AuditRecord | RegisterAuditRecord | RegisterAuditRecord | none → Registered | AuditRecordRegistered | Lifecycle transition owned by Observability Authority. |
| AuditRecord | ValidateEvidence | ValidateEvidence | Registered → Validated | EvidenceValidated | Lifecycle transition owned by Observability Authority. |
| AuditRecord | ApplyRetentionPolicy | ApplyRetentionPolicy | Validated → Retained | RetentionApplied | Lifecycle transition owned by Observability Authority. |
| AuditRecord | ArchiveEvidence | ArchiveEvidence | Retained → Archived | AuditRecordArchived | Lifecycle transition owned by Observability Authority. |
