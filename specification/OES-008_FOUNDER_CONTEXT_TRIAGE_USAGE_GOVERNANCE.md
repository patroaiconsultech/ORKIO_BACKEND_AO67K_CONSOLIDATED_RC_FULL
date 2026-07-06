# OES-008 — Founder Context Triage & Usage Governance

**Title:** Founder Context Triage & Usage Governance  
**Version:** 0.1-rc-r4  
**Status:** Release Candidate  
**Owner:** Chief Architecture & Engineering Officer (AO-01)  
**Approver:** Vision Owner + Independent Engineering Auditor  
**Release Candidate:** OES-RC-0005-R4

## Dependencies

* OES-001 — Engineering Constitution (Baseline)
* OES-002 — Engineering Glossary (Baseline)
* OES-003 — Engineering Governance (Baseline)
* OES-004 — Engineering Delivery Standard (Baseline)
* OES-005 — Canonical Domain Model (Baseline / OES-RC-0002-R4)
* OES-006 — Capability Catalog (Baseline / OES-RC-0003-R3)
* OES-007 — Contract and Event Projection (Baseline / OES-RC-0004-R1)
* OES-006 document SHA-256: `C17580C10C773B5D7917D35DE6A90C62919CA14A2670E4222AE971492CC3FC64`
* OES-007 document SHA-256: `C67F471AAA59D0EAF57F791ED43679D0714D990903CC927A4FAE18DCD8A88B26`
* OES-007 applied backend ZIP SHA-256: `06F36CCA65130F685FF47821C1B5ABE484F60996EEEEAB1A0B7E1A82C22A39C1`
* OES-RC-0004-R1 repo-ready ZIP SHA-256: `68BB3092CF54758597E5A90A8C6016397CCB6BC5CAD23321CBF728537E0E9A28`

## Objective

Define the normative governance layer for triaging founder-provided context before it is used by ORKIO, Patroai, agents, documentation, prompts, runtime design or public repositories.

OES-008 does **not** ingest private data. It defines how private, partial or sensitive founder context must be classified, sanitized, authorized, audited and converted into safe learning signals before any usage.

## Core Principle

Founder context is denied by default.

No private source may be used, published, embedded into an agent, inserted into runtime, transformed into memory, converted into prompt material or promoted into documentation until it passes through the Private Context Triage Layer.

## Learning Principle

The system may learn from errors, corrections, successful decisions and audit outcomes only through sanitized operational signals.

Allowed learning is limited to abstract metadata such as: decision status, finding severity, control gap type, remediation class, validation result and approved lesson identifier.

Prohibited learning includes raw private text, family details, emotional content, financial details, health details, private links, account identifiers, credentials, exports, conversation bodies or any source content that has not been sanitized and authorized.

The system must learn the **pattern**, never expose or memorize the **private substance**.

## Scope

This release candidate is specification-only.

It defines:

1. the Private Context Triage Layer;
2. context classification classes;
3. usage authorization rules;
4. public/private boundary rules;
5. source register rules for private source candidates;
6. sanitization and minimization rules;
7. safe learning-signal rules;
8. stronger audit gates for future ingestion.

## Non-goals

* Do not ingest raw ChatGPT exports.
* Do not ingest Google Drive files.
* Do not publish private source content.
* Do not create runtime memory.
* Do not modify agents.
* Do not alter API, database or infrastructure.
* Do not train, fine-tune or seed model memory.
* Do not include personal, emotional, financial, health, family or strategic raw content in this repository.
* Do not treat partial private files as canonical truth.
* Do not claim authorization from metadata-only registration.

## Private Context Triage Layer

The approved flow is:

```text
Private source candidate
        ↓
Source registration using metadata only
        ↓
No content access by default
        ↓
Classification
        ↓
Sanitization / minimization
        ↓
Usage authorization
        ↓
Audit record
        ↓
Approved context artifact
        ↓
Purpose-bound usage
        ↓
Sanitized learning signal, when applicable
```

A private source candidate can include:

* a partial document stored in a private drive;
* an exported conversation archive;
* a founder biography draft;
* strategy notes;
* chat-derived context;
* investor or corporate planning notes;
* private memory material.

A source candidate is never equivalent to approved context.

## Context Classification Classes

| Class | Meaning | Default publication state |
|---|---|---|
| `PUBLIC` | Safe for public documents and repositories after sanitization and approval. | Allowed only after approval |
| `INTERNAL` | Usable inside ORKIO/Patroai operations, not public. | Not public |
| `FOUNDER_PRIVATE` | May inform human decisions but must not become public or runtime context. | Not public |
| `SENSITIVE` | Must be excluded, minimized or redacted. | Prohibited |
| `STRATEGIC_CONFIDENTIAL` | Business, IP, fundraising or competitive strategy. | Prohibited |
| `DO_NOT_USE` | Explicitly excluded from all usage. | Prohibited |

## Usage Rules

| Rule | Requirement |
|---|---|
| Deny by default | Every source candidate starts as unusable. |
| Metadata-only registration | A private source can be registered by ID, type and status without opening or ingesting content. |
| No raw publication | Raw private context must never be committed to a public repo. |
| Purpose binding | Approved context must state its exact allowed use. |
| Minimum necessary | Use the smallest safe summary, never full private text. |
| Founder approval | Approval is mandatory before promotion. |
| Learning without exposure | Lessons may be stored only as sanitized operational signals. |

## Current Source Candidate Handling

`FOUNDER_CONTEXT_PARTIAL_GDRIVE_001` is registered only as a private source candidate.

Current use is limited to:

```text
metadata_only_without_content_access
```

This means the system may know that a partial private source exists and that it requires triage. It may not read, summarize, ingest, quote, index, publish, embed, train on or use the source content.

## Audit Gates

Before any future usage of private founder context, the following gates must pass:

1. source is registered without raw content;
2. source candidate schema validates with closed properties;
3. publication is explicitly false while the item is a source candidate;
4. founder approval is required before any use;
5. privacy boundary scan passes across all textual files;
6. no private links, credentials, e-mails, account identifiers or raw source fields are present;
7. collision check is executed against the commit-target baseline;
8. learning signals contain only sanitized metadata and no private source content.

## Release Candidate R3 Corrections

OES-RC-0005-R4 fixes the READONLY_AUDIT YELLOW findings from OES-RC-0005-R1:

* disambiguates OES-007 document SHA from OES-007 backend ZIP SHA;
* changes partial private source current use to `metadata_only_without_content_access`;
* strengthens privacy scanning across Markdown, JSON, YAML, TXT and Python files;
* closes the source-candidate JSON schema;
* fixes publication and approval constraints for source candidates;
* replaces nominal collision validation with baseline-aware collision validation;
* adds a safe learning-signal policy so the system can learn from outcomes without exposing sensitive data.
