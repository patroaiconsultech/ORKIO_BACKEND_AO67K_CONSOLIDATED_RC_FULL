# OES-RC-0005-R4 Release Notes

OES-RC-0005-R4 is a specification-only correction release for Founder Context Triage & Usage Governance.

It hardens the governance layer so ORKIO can learn from engineering outcomes without exposing private founder content.

The package is intended for READONLY_AUDIT before publication.


## R3 scope

R3 is a procedural patch over R2. It keeps the founder-context privacy governance unchanged and fixes only audit reproducibility and baseline authentication.


## R4 Procedural Fixes

* Validators normalize paths using POSIX separators for Windows/POSIX reproducibility.
* Backend-applied ZIP is regenerated without nested handoff/audit ZIP contamination.
* Central privacy, deny-by-default and learning-signal policies are unchanged.
