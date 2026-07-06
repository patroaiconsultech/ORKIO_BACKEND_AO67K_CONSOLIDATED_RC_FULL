# OES-RC-0005-R4 Validation Checklist

- [ ] Confirm repo-ready ZIP SHA-256.
- [ ] Confirm OES-007 baseline backend SHA-256.
- [ ] Confirm OES-007 document SHA-256 separately.
- [ ] Confirm all files are under `/specification`.
- [ ] Confirm no runtime/API/DB/infra files changed.
- [ ] Run manifest check.
- [ ] Run classification check.
- [ ] Run privacy boundary check.
- [ ] Run scope check.
- [ ] Run collision check against target baseline.
- [ ] Confirm no private content, private links, e-mails, account exports or credentials.
- [ ] Confirm Google Drive source candidate is metadata-only without content access.
- [ ] Confirm safe learning-signal policy is present.
- [ ] Emit GREEN/YELLOW/RED and GO/NO-GO.


## R4 Procedural Fixes

* Validators normalize paths using POSIX separators for Windows/POSIX reproducibility.
* Backend-applied ZIP is regenerated without nested handoff/audit ZIP contamination.
* Central privacy, deny-by-default and learning-signal policies are unchanged.
