# Sanitization and Minimization Rules

Release Candidate: OES-RC-0005-R4

## Minimum Necessary Rule

Use the smallest safe abstraction required for the allowed purpose.

## Required Redactions

Before any content can be promoted out of private triage, remove or generalize:

* account identifiers;
* private links;
* credentials or tokens;
* e-mail addresses;
* personal identifiers not required for the approved purpose;
* financial, medical, family and emotional details;
* raw conversation bodies;
* private strategy details not approved for the destination.

## Approved Output Types

| Output type | Condition |
|---|---|
| Sanitized public summary | PUBLIC classification and founder approval |
| Internal summary | INTERNAL classification and founder approval |
| Strategic note | STRATEGIC_CONFIDENTIAL classification and restricted access |
| Human-only note | FOUNDER_PRIVATE classification and no runtime use |
| Learning signal | No sensitive content and no raw source text |
