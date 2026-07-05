# Bounded Context Map

| Context | Aggregate Root | Authority | Notes |
|---|---|---|---|
| Identity | Organization | Governance Authority | Institutional boundary, workspaces, people and memberships. |
| Knowledge | KnowledgeAsset | Knowledge Authority | Institutional knowledge assets, provenance and classification. |
| Agent | Agent | Capability Authority | Operational agents and capability bindings. |
| Conversation | Conversation | Runtime Authority | Contextual continuity and messages. |
| Decision | Decision | Decision Authority | Governed business decisions. |
| Execution | Execution | Runtime Authority | Governed operational execution. |
| Governance | Policy | Governance Authority | Policies, rules, authorities, delegations. |
| Observability | AuditRecord | Observability Authority | Business evidence and audit trail. |

## Cross-Context Rule

Contexts may reference each other only through references. References do not transfer ownership.
