# Release gates

## Gate R1 — Preview

```text
boot_canary=MZ-001-R1
anonymous=401
non_admin=403
tenant_mismatch=403
admin_preview=200
candidate_count_validated=true
database_delta=0
dry_run_false=403
db_unavailable=503
```

## Gate R1.1 — Tenant hardening

```text
proposal_list_cross_tenant=403
proposal_detail_cross_tenant=404_or_403
approve_cross_tenant=404_or_403
reject_cross_tenant=404_or_403
execution_list_cross_tenant=403
```

## Gate R2 — Escrita governada

```text
feature_flag_false=403
approved_false=409
digest_mismatch=409
candidate_count_changed=409
idempotent_retry=same_receipt
single_transaction=true
audit_created=true
cross_tenant_delta=0
```

## Gate R3 — KPI confiável

```text
metric_sources_declared=true
sample_count_declared=true
confidence_declared=true
measured_at_declared=true
classification_declared=true
overall_excludes_unmeasured=true
baseline_id_declared=true
```
