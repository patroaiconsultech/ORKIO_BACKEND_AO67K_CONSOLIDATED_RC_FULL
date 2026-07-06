# Public / Private Boundary

Release Candidate: OES-RC-0005-R4

## Public Repository Boundary

The public repository may contain:

* policies;
* schemas;
* sanitized templates;
* audit gates;
* empty registers or metadata-only source candidates;
* manifests and hashes.

The public repository must not contain:

* raw private source content;
* private-drive links;
* account exports;
* credentials;
* private conversation bodies;
* personal, family, health, financial or emotional details;
* unapproved strategy excerpts.

## Boundary Enforcement

The privacy boundary checker scans textual files across the package and primary OES-008 document. It looks for private links, e-mails, credential-like tokens, raw-content fields and other sensitive indicators.

The check is not a substitute for human review, but it is required to prevent obvious leakage before audit.
