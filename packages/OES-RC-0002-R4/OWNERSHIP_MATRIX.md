# Ownership Matrix

| Concept | Type | Owner | Referenced By | Rule |
|---|---|---|---|---|
| Organization | Aggregate Root | Governance Authority | All aggregates | Owns institutional boundary. |
| Workspace | Entity | Governance Authority | Conversation, Agent, Knowledge | Operational boundary. |
| Role | Value Object | Governance Authority | Membership, Policy | Classification only; does not grant permission. |
| KnowledgeAsset | Aggregate Root | Knowledge Authority | Conversation, Decision, Execution | Institutional knowledge asset. |
| Classification | Value Object | Knowledge Authority | KnowledgeAsset | Access meaning, not ownership. |
| Provenance | Value Object | Knowledge Authority | KnowledgeAsset | Immutable lineage. |
| Agent | Aggregate Root | Capability Authority | Conversation, Execution | Executes authorized capabilities. |
| RuntimeContext | Value Object | Runtime Authority | Agent, Conversation | Transient context, no ownership mutation. |
| Conversation | Aggregate Root | Runtime Authority | Decision, Execution | Context container, not knowledge owner. |
| Decision | Aggregate Root | Decision Authority | Execution, AuditRecord | Primary business artifact. |
| DecisionEvidence | Entity | Decision Authority | Decision | Owned evidence representation. |
| EvidenceReference | Value Object | Decision Authority | Decision | Reference only, not evidence ownership. |
| Execution | Aggregate Root | Runtime Authority | AuditRecord, Knowledge | Governed action. |
| ExecutionEvidence | Entity | Runtime Authority | Execution, Observability | Execution-owned evidence. |
| Artifact | Entity | Runtime Authority | Knowledge | Requires promotion to KnowledgeAsset. |
| Policy | Aggregate Root | Governance Authority | All aggregates | Governs rules and authorities. |
| PolicyVersion | Value Object | Governance Authority | Policy | Version metadata. |
| AuditRecord | Aggregate Root | Observability Authority | All aggregates | Business evidence record. |
| AuditEvidence | Entity | Observability Authority | AuditRecord | Audit-owned evidence representation. |
| AuditScope | Value Object | Observability Authority | AuditRecord | Scope metadata. |
| Correlation | Value Object | Observability Authority | AuditRecord | Correlation metadata. |
| ExecutionHistory | Removed | none | Agent via AuditRecordReference | Not an Agent-owned entity. |

## Reference Ownership Matrix

| Reference | Target Concept | Owning Authority | Rule |
|---|---|---|---|
| OrganizationReference | Organization | Governance Authority | Reference only; no mutation. |
| WorkspaceReference | Workspace | Governance Authority | Reference only; no mutation. |
| KnowledgeAssetReference | KnowledgeAsset | Knowledge Authority | Reference only; no mutation. |
| AgentReference | Agent | Capability Authority | Reference only; no mutation. |
| CapabilityReference | Capability | Capability Authority | Reference only; no mutation. |
| ConversationReference | Conversation | Runtime Authority | Reference only; no mutation. |
| DecisionReference | Decision | Decision Authority | Reference only; no mutation. |
| ExecutionReference | Execution | Runtime Authority | Reference only; no mutation. |
| PolicyReference | Policy | Governance Authority | Reference only; no mutation. |
| AuditRecordReference | AuditRecord | Observability Authority | Reference only; no mutation. |
