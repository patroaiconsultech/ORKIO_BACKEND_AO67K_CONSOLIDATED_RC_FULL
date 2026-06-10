# AO67K/AO67L Consolidated Release Candidate

This package was generated for staging/parallel deployment validation only.

Not production-deployed by ChatGPT.
No commit/branch/PR/deploy has been performed.

Required runtime flags for first validation:
- ORKIO_PUBLIC_CHAT_GATEWAY_ENABLED=true
- ORKIO_JOURNEY_MEMORY_COMMIT_ENABLED=false
- ORKIO_CONTACT_EMAIL_REQUIRED=false

Rollback:
- Set ORKIO_PUBLIC_CHAT_GATEWAY_ENABLED=false for chat gateway rollback.
- Revert to original production zips for full physical rollback.

See external files:
- AO67K_L_CONSOLIDATED_RC_REPORT.md
- AO68_STAGING_DEPLOYMENT_MATRIX.txt
- AO67K_L_ROLLBACK.md
