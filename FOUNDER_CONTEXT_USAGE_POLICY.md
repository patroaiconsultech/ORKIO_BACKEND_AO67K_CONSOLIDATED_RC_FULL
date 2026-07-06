# Founder Context Usage Policy

Release Candidate: OES-RC-0005-R4

## Default Rule

All founder context is denied by default.

A context item becomes usable only after registration, classification, sanitization, authorization and audit logging.

## Source Candidate Rule

A private source candidate can be registered without opening its content.

For source candidates:

* `raw_content_included` must be `false`;
* `direct_publication_allowed` must be `false`;
* `requires_founder_approval_before_use` must be `true`;
* `content_access_allowed` must be `false`;
* `allowed_current_use` must be either `none` or `metadata_only_without_content_access`.

## Allowed Usage Types After Approval

| Usage type | Requirement |
|---|---|
| Public founder narrative | Must be classified as `PUBLIC`, sanitized and approved. |
| Internal project continuity | Must be classified as `INTERNAL`, sanitized and approved. |
| Strategic planning | Must be classified as `STRATEGIC_CONFIDENTIAL`, minimized and access-controlled. |
| Human-only guidance | Must be classified as `FOUNDER_PRIVATE` and kept out of runtime memory. |
| Excluded material | Must be classified as `DO_NOT_USE`. |

## Prohibited Usage

The following are prohibited without a future approved implementation gate:

* raw ChatGPT export ingestion;
* raw private drive ingestion;
* private conversation indexing;
* automatic agent memory seeding;
* public repository commit of private material;
* use of partial private documents as canonical fact;
* use of sensitive material in test fixtures or examples;
* learning from source content that has not been sanitized and authorized.

## Runtime Boundary

Future runtime systems must treat this policy as a guardrail. No handler, agent, retriever, memory store or prompt builder may use founder context unless a usage authorization exists.
