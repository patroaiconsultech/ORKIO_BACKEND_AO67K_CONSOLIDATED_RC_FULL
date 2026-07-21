# ORKIO Evolution Intelligence Premium R1.6

This release is a **cumulative delta over Premium R1.4**.

It includes:

1. every file introduced or modified by Evolution Intelligence Foundation R1.5;
2. the Premium Lineage and Governance hardening introduced in R1.6;
3. migrations `0039` and `0040` in the correct order;
4. no implicit file deletions;
5. no automatic code write, commit, merge, deploy or proposal application.

The R1.5 package does **not** need to be applied first.

## Application boundary

Extract the delta at the backend repository root.

Expected base artifact:

```text
ORKIO_BACKEND_PREMIUM_R14_ROOT_UPLOAD.zip
sha256=5f75d055884eb67e2508f7740a1bf06a2eeb701ee1e5a0403ac45ccfead103bd
```

Git branch and commit remain `NOT_PROVEN` until the delta is reviewed against
the current repository HEAD.

## Safety defaults

```text
proposal_only=true
write_enabled=false
auto_apply_enabled=false
human_approval_required=true
rollback_required=true
```

## Mandatory staging gate

Production remains blocked until validation with real PostgreSQL, Railway
release identity, two tenants and the platform SSE smoke.
