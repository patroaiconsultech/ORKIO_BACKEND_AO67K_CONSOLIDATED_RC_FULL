# State Machine Matrix

| Aggregate | Source State | Contract | Target State | Event | Authority |
|---|---|---|---|---|---|
| Organization | none | CreateOrganization | Draft | OrganizationCreated | Governance Authority |
| Organization | Draft | ActivateOrganization | Active | OrganizationActivated | Governance Authority |
| Organization | Active | SuspendOrganization | Suspended | OrganizationSuspended | Governance Authority |
| Organization | Active/Suspended | ArchiveOrganization | Archived | OrganizationArchived | Governance Authority |
| Membership | none | InviteMember | Pending | MemberInvited | Governance Authority |
| Membership | Pending | ActivateMembership | Active | MembershipActivated | Governance Authority |
| Membership | Active | SuspendMembership | Suspended | MembershipSuspended | Governance Authority |
| Membership | Active/Suspended | RevokeMembership | Revoked | MembershipRevoked | Governance Authority |
| KnowledgeAsset | none | CreateKnowledgeAsset | Draft | KnowledgeAssetCreated | Knowledge Authority |
| KnowledgeAsset | Draft | ValidateKnowledgeAsset | Validated | KnowledgeAssetValidated | Knowledge Authority |
| KnowledgeAsset | Validated | ApproveKnowledgeAsset | Approved | KnowledgeAssetApproved | Knowledge Authority |
| KnowledgeAsset | Approved | OperationalizeKnowledgeAsset | Operational | KnowledgeAssetOperationalized | Knowledge Authority |
| KnowledgeAsset | Any non-Archived | ArchiveKnowledgeAsset | Archived | KnowledgeAssetArchived | Knowledge Authority |
| Agent | none | CreateAgent | Draft | AgentCreated | Capability Authority |
| Agent | Draft | ApproveAgent | Approved | AgentApproved | Capability Authority |
| Agent | Approved | ActivateAgent | Active | AgentActivated | Capability Authority |
| Agent | Active | SuspendAgent | Suspended | AgentSuspended | Capability Authority |
| Agent | Approved/Suspended | ArchiveAgent | Archived | AgentArchived | Capability Authority |
| Conversation | none | OpenConversation | Created | ConversationCreated | Runtime Authority |
| Conversation | Created/Active | AppendMessage | Active | MessageRecorded | Runtime Authority |
| Conversation | Active | PauseConversation | Paused | ConversationPaused | Runtime Authority |
| Conversation | Paused | ResumeConversation | Active | ConversationResumed | Runtime Authority |
| Conversation | Active/Paused | CloseConversation | Closed | ConversationClosed | Runtime Authority |
| Conversation | Closed | ArchiveConversation | Archived | ConversationArchived | Runtime Authority |
| Decision | none | CreateDecision | Draft | DecisionCreated | Decision Authority |
| Decision | Draft | AttachEvidence | Draft | EvidenceAttached | Decision Authority |
| Decision | Draft | SubmitDecisionReview | Under Review | DecisionSubmitted | Decision Authority |
| Decision | Under Review | ApproveDecision | Approved | DecisionApproved | Decision Authority |
| Decision | Under Review | RejectDecision | Rejected | DecisionRejected | Decision Authority |
| Decision | Approved | PublishDecision | Effective | DecisionPublished | Decision Authority |
| Decision | Effective | SupersedeDecision | Superseded | DecisionSuperseded | Decision Authority |
| Decision | Rejected/Effective/Superseded | ArchiveDecision | Archived | DecisionArchived | Decision Authority |
| Execution | none | PlanExecution | Planned | ExecutionPlanned | Runtime Authority |
| Execution | Planned | AuthorizeExecution | Authorized | ExecutionAuthorized | Runtime Authority |
| Execution | Authorized | StartExecution | Running | ExecutionStarted | Runtime Authority |
| Execution | Running | CompleteExecution | Completed | ExecutionCompleted | Runtime Authority |
| Execution | Completed | VerifyExecution | Verified | ExecutionVerified | Runtime Authority |
| Execution | Verified | ArchiveExecution | Archived | ExecutionArchived | Runtime Authority |
| Execution | Completed/Verified | PromoteArtifactToKnowledge | KnowledgeAsset Draft | ArtifactPromotionRequested / KnowledgeAssetCreated | Knowledge Authority |
| Policy | none | CreatePolicy | Draft | PolicyCreated | Governance Authority |
| Policy | Draft | SubmitPolicyReview | Under Review | PolicySubmitted | Governance Authority |
| Policy | Under Review | ApprovePolicy | Approved | PolicyApproved | Governance Authority |
| Policy | Under Review | RejectPolicy | Rejected | PolicyRejected | Governance Authority |
| Policy | Approved | PublishPolicy | Effective | PolicyPublished | Governance Authority |
| Policy | Effective | SupersedePolicy | Superseded | PolicySuperseded | Governance Authority |
| Policy | Rejected/Effective/Superseded | ArchivePolicy | Archived | PolicyArchived | Governance Authority |
| Delegation | Active | RevokeDelegation | Revoked | DelegationRevoked | Governance Authority |
| AuditRecord | none | RegisterAuditRecord | Registered | AuditRecordRegistered | Observability Authority |
| AuditRecord | Registered | ValidateEvidence | Validated | EvidenceValidated | Observability Authority |
| AuditRecord | Validated | ApplyRetentionPolicy | Retained | RetentionApplied | Observability Authority |
| AuditRecord | Retained | ArchiveEvidence | Archived | AuditRecordArchived | Observability Authority |

## Coverage

This matrix is normative and intended to be complete for OES-RC-0002-R4.
