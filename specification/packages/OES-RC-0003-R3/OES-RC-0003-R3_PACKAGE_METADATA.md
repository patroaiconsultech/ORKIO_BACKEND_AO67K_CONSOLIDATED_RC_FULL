# OES-RC-0003-R3 — Package Metadata

| Field | Value |
|---|---|
| Package ID | OES-RC-0003-R3 |
| Title | OES-006 Capability Catalog R3 |
| Status | Release Candidate |
| Owner | Chief Architecture & Engineering Officer (AO-01) |
| Approver | Vision Owner + Independent Engineering Auditor |
| Source Baseline | OES-RC-0002-R4 |
| Source Baseline SHA-256 | `4273278F9786F1E9F0EE86CB4F5D8577B47BA76C44866C16676C85738A66A20A` |
| Patch Base Package | OES-RC-0003-R2 |
| Patch Base Package SHA-256 | `8DEBA4E0C48E5DA758FFB382213705CA0234BF2125C37B81DB6220A8054E3366` |
| Patch Base OES-006 Preimage SHA-256 | `B3267359FE6BF3B07C28F390EF963814AA2EE40A860361048368E68CD972ABE6` |
| Prior Rejected OES-006 Preimage SHA-256 | `3391510CF4F03C95B4793ACD063FAC430CE6B367480473AAC92DEA7D97091684` |
| Target Repository | https://github.com/patroaiconsultech/ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL |
| Runtime Code Included | No |
| Validation Tooling Included | Yes |
| Expected Capabilities | 56 |
| Reconstructed Capabilities | 56 |
| OES-006 Output SHA-256 | `C17580C10C773B5D7917D35DE6A90C62919CA14A2670E4222AE971492CC3FC64` |
| Intentional Replacements | `specification/OES-006_CAPABILITY_CATALOG.md` only when target preimage hash matches one of the declared allowed preimages |

## Collision Policy

All collisions are blocked unless the target path is explicitly listed in `intentional_replacements` and its current file hash matches a declared preimage hash.

The only intentional replacement is:

```text
specification/OES-006_CAPABILITY_CATALOG.md
```

It may be replaced only if the target file hash is one of:

```text
3391510CF4F03C95B4793ACD063FAC430CE6B367480473AAC92DEA7D97091684
B3267359FE6BF3B07C28F390EF963814AA2EE40A860361048368E68CD972ABE6
```

If the target file does not exist, the package may create it. If the target exists with any other hash, the collision check MUST fail.

## Patch Scope

OES-RC-0003-R3 applies only the final OES-006 release-engineering patch set:

- Vocabulary Closure for Produced References.
- Produced References validator against canonical reference inventory.
- Replacement/preimage policy alignment.
- Editorial cleanup and R3 package identity consistency.

Runtime code, contracts, events and canonical domain baseline are out of scope.
