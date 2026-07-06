# Learning Signals Policy

Release Candidate: OES-RC-0005-R4

## Purpose

Allow ORKIO to improve from errors, audit findings, successful validations and founder decisions without exposing sensitive content.

## Core Rule

The system learns from sanitized operational signals, not from raw private content.

## Allowed Learning Signals

| Signal | Example |
|---|---|
| `audit_state` | GREEN, YELLOW, RED |
| `decision` | GO, NO-GO |
| `finding_severity` | P1, P2, P3 |
| `control_gap_type` | nominal_check, custody_mismatch, privacy_boundary_gap |
| `remediation_class` | schema_hardening, manifest_fix, boundary_tightening |
| `validation_result` | PASS, FAIL |
| `lesson_id` | LESSON-OES008-R3-001 |

## Prohibited Learning Inputs

The following must not be used as learning inputs unless independently sanitized, minimized and approved:

* raw conversation bodies;
* raw private-drive text;
* exports from private accounts;
* private links;
* credentials, tokens or account identifiers;
* e-mail addresses;
* financial, health, family or emotional details;
* private strategy text;
* unapproved founder biography material;
* any field named or functioning as raw source content.

## Learning Pipeline

```text
Audit outcome / operational event
        ↓
Signal extraction
        ↓
Privacy boundary scan
        ↓
Sanitization
        ↓
Founder approval, when context-derived
        ↓
Lesson ID assignment
        ↓
Purpose-bound reuse
```

## Safe Lesson Format

A safe lesson may contain:

```json
{
  "lesson_id": "LESSON-OES008-R3-001",
  "source_event_type": "readonly_audit",
  "audit_state": "YELLOW",
  "control_gap_type": "nominal_check",
  "remediation_class": "checker_hardening",
  "sensitive_content_included": false,
  "allowed_reuse": ["engineering_methodology", "future_gate_design"]
}
```

A safe lesson must not contain private excerpts, private links, personal identifiers, credentials or raw source text.

## Application to OES-RC-0005-R4

The R3 package learns from the R1 audit by improving gates and policies. It does not include the private source content that motivated the governance discussion.
