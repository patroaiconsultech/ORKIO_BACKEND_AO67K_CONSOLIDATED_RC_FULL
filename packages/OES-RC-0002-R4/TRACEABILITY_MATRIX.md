# Traceability Matrix

| Source | Element | Consumer | Rule |
|---|---|---|---|
| OES-001 | Engineering principles | OES-005 | Domain remains implementation-independent. |
| OES-002 | Canonical vocabulary | OES-005 | Terms are specialized, not redefined. |
| OES-003 | Authorities | OES-005 | Each aggregate has one owning authority. |
| OES-004 | Delivery standard | OES-RC-0002-R4 | Package metadata, manifest, preflight and audit request are package-scoped. |
| DOM-040 | Decision | OES-006/OES-007/OES-008 | Capabilities, contracts and events derive from state machine. |
| INV-DEC-004 | Decision immutability | OES-009 | Runtime must preserve approved business content. |
| INV-OBS-002 | Audit immutability | OES-009/OES-010 | Runtime and Knowledge must preserve evidential payload. |
| STATE_MACHINE_MATRIX | Transitions | OES-006/OES-007/OES-008 | No transition invented downstream. |
| OWNERSHIP_MATRIX | Ownership | OES-007/OES-009 | No aggregate mutates foreign entities. |
| CAPABILITY_MATRIX | Capabilities | OES-006 | Capability catalog derives from this matrix. |
| DERIVATION_MATRIX | Capability → Contract → Event | OES-007/OES-008/OES-009 | Downstream chain is traceable. |
