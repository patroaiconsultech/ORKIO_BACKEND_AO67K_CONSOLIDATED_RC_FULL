# Domain Decision Matrix

| Aggregate | Root | Authority | Lifecycle Coverage | Ownership Status |
|---|---|---|---|---|
| Identity | Organization | Governance Authority | Complete | Owns Organization, Workspace, Person, Membership; Role is Value Object. |
| Knowledge | KnowledgeAsset | Knowledge Authority | Complete | Owns Knowledge entities; Classification, Provenance and KnowledgeVersion are Value Objects. |
| Agent | Agent | Capability Authority | Complete | Owns AgentProfile and CapabilityBinding; execution history is Observability reference. |
| Conversation | Conversation | Runtime Authority | Complete | Owns messages/participants/attachments; references knowledge, decisions and executions. |
| Decision | Decision | Decision Authority | Complete | Owns DecisionEvidence; references external evidence through EvidenceReference. |
| Execution | Execution | Runtime Authority | Complete | Owns ExecutionEvidence and Artifacts; promotion to Knowledge requires Knowledge Authority. |
| Governance | Policy | Governance Authority | Complete | Owns policies, rules, authorities and delegations. |
| Observability | AuditRecord | Observability Authority | Complete | Owns AuditEvidence and audit references. |
