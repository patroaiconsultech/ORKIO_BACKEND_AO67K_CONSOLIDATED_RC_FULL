# Capability Matrix

This matrix is normative and complete for OES-RC-0002-R4.

| Capability | Aggregate | Authority | Inputs | Outputs | Acceptance |
|---|---|---|---|---|---|
| CreateOrganization | Organization | Governance Authority | Organization profile | Organization Draft | Unique organization ID exists. |
| ActivateOrganization | Organization | Governance Authority | Organization Draft | Organization Active | Activation recorded. |
| SuspendOrganization | Organization | Governance Authority | Organization Active | Organization Suspended | Suspension rationale recorded. |
| ArchiveOrganization | Organization | Governance Authority | Organization terminal | Organization Archived | Retention preserved. |
| InviteMember | Membership | Governance Authority | Person, Organization | Membership Pending | Invitation auditable. |
| ActivateMembership | Membership | Governance Authority | Membership Pending | Membership Active | Membership active. |
| SuspendMembership | Membership | Governance Authority | Membership Active | Membership Suspended | Suspension recorded. |
| RevokeMembership | Membership | Governance Authority | Membership Active/Suspended | Membership Revoked | Participation revoked. |
| CreateKnowledgeAsset | KnowledgeAsset | Knowledge Authority | Source, classification | KnowledgeAsset Draft | Source and classification exist. |
| ValidateKnowledgeAsset | KnowledgeAsset | Knowledge Authority | Draft Asset | Validated Asset | Validation evidence recorded. |
| ApproveKnowledgeAsset | KnowledgeAsset | Knowledge Authority | Validated Asset | Approved Asset | Approval auditable. |
| OperationalizeKnowledgeAsset | KnowledgeAsset | Knowledge Authority | Approved Asset | Operational Asset | Authorized use enabled. |
| ArchiveKnowledgeAsset | KnowledgeAsset | Knowledge Authority | Asset | Archived Asset | Provenance retained. |
| CreateAgent | Agent | Capability Authority | AgentProfile | Agent Draft | Agent identity exists. |
| ApproveAgent | Agent | Capability Authority | Agent Draft | Agent Approved | Approval recorded. |
| BindCapability | Agent | Capability Authority | Agent, Capability | CapabilityBinding | Binding authorized. |
| ActivateAgent | Agent | Capability Authority | Agent Approved | Agent Active | Agent active. |
| SuspendAgent | Agent | Capability Authority | Agent Active | Agent Suspended | Execution disabled. |
| ArchiveAgent | Agent | Capability Authority | Agent | Agent Archived | Agent inactive and auditable. |
| OpenConversation | Conversation | Runtime Authority | Workspace, participant | Conversation Created | Context ID exists. |
| AppendMessage | Conversation | Runtime Authority | Conversation, message | Message | Message belongs to conversation. |
| ResolveContext | Conversation | Runtime Authority | Conversation | ContextSnapshot | Context authorized. |
| PauseConversation | Conversation | Runtime Authority | Active Conversation | Paused Conversation | Pause recorded. |
| ResumeConversation | Conversation | Runtime Authority | Paused Conversation | Active Conversation | Resume recorded. |
| CloseConversation | Conversation | Runtime Authority | Active/Paused Conversation | Closed Conversation | Conversation closed. |
| ArchiveConversation | Conversation | Runtime Authority | Closed Conversation | Archived Conversation | Context retained. |
| CreateDecision | Decision | Decision Authority | Context, rationale | Decision Draft | Draft has context. |
| AttachEvidence | Decision | Decision Authority | Decision, EvidenceReference | Decision with evidence | Reference valid. |
| SubmitDecisionReview | Decision | Decision Authority | Draft Decision | Under Review Decision | Evidence/rationale complete. |
| ApproveDecision | Decision | Decision Authority | Under Review Decision | Approved Decision | Approval recorded. |
| RejectDecision | Decision | Decision Authority | Under Review Decision | Rejected Decision | Rationale recorded. |
| PublishDecision | Decision | Decision Authority | Approved Decision | Effective Decision | Effective metadata recorded. |
| SupersedeDecision | Decision | Decision Authority | Effective Decision, new Decision | Superseded Decision | Supersession reference recorded. |
| ArchiveDecision | Decision | Decision Authority | Terminal Decision | Archived Decision | Auditability preserved. |
| PlanExecution | Execution | Runtime Authority | Decision/Policy | Execution Planned | Authorizer referenced. |
| AuthorizeExecution | Execution | Runtime Authority | Execution Planned | Execution Authorized | Authorization recorded. |
| StartExecution | Execution | Runtime Authority | Execution Authorized | Execution Running | Running state recorded. |
| CompleteExecution | Execution | Runtime Authority | Execution Running | Execution Completed | Result/evidence recorded. |
| VerifyExecution | Execution | Runtime Authority | Execution Completed | Execution Verified | Evidence exists. |
| ArchiveExecution | Execution | Runtime Authority | Execution Verified | Execution Archived | Audit trail preserved. |
| PromoteArtifactToKnowledge | Execution/Knowledge | Knowledge Authority | Artifact, provenance | KnowledgeAsset Draft | Promotion uses Knowledge capability. |
| CreatePolicy | Policy | Governance Authority | Scope, rules | Policy Draft | Policy ID and scope exist. |
| SubmitPolicyReview | Policy | Governance Authority | Policy Draft | Policy Under Review | Review recorded. |
| ApprovePolicy | Policy | Governance Authority | Policy Under Review | Policy Approved | Approval recorded. |
| RejectPolicy | Policy | Governance Authority | Policy Under Review | Policy Rejected | Rejection rationale recorded. |
| PublishPolicy | Policy | Governance Authority | Policy Approved | Policy Effective | Effective period recorded. |
| SupersedePolicy | Policy | Governance Authority | Policy Effective, new Policy | Policy Superseded | Supersession recorded. |
| DelegateAuthority | Policy | Governance Authority | Authority, delegate, scope | Delegation | Delegation valid period exists. |
| RevokeDelegation | Policy | Governance Authority | Delegation | Delegation Revoked | Revocation recorded. |
| ArchivePolicy | Policy | Governance Authority | Policy terminal | Policy Archived | Policy auditable. |
| RegisterAuditRecord | AuditRecord | Observability Authority | Context, evidence | AuditRecord Registered | Payload immutable. |
| ValidateEvidence | AuditRecord | Observability Authority | AuditRecord | AuditRecord Validated | Validation metadata recorded. |
| CorrelateEvidence | AuditRecord | Observability Authority | AuditRecords | Correlation | Origins referenced. |
| ApplyRetentionPolicy | AuditRecord | Observability Authority | AuditRecord | AuditRecord Retained | Retention applied. |
| ArchiveEvidence | AuditRecord | Observability Authority | AuditRecord Retained | AuditRecord Archived | Evidence retrievable. |
