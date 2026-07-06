# Usage Authorization Workflow

Release Candidate: OES-RC-0005-R4

## Required Steps

1. Register source metadata.
2. Confirm raw content is not included in the repository.
3. Classify the source.
4. Sanitize or minimize.
5. Define exact purpose.
6. Define allowed destinations.
7. Obtain founder approval.
8. Record the audit decision.
9. Only then promote to an approved context artifact.

## Forbidden Shortcut

A source being useful, known, referenced or available does not authorize its use.

## Required Decision Record

Every authorization record must include:

* source ID;
* classification;
* purpose;
* allowed destinations;
* disallowed destinations;
* sanitization summary;
* approval status;
* approver;
* auditor;
* timestamp;
* whether sensitive content is included.

The default status is `PENDING`.
