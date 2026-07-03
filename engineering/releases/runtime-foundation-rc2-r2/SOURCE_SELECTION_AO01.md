# AO-01 Source Selection

## Selected

- `ORKIO_CORE_RC1_EPIC002B_R1_CANONICAL_ASSISTANT_MESSAGE_ID_SHADOW_LOCKED.zip`
  - selected for canonical JSON serialization and 12-test persistence suite
  - `app/config/*` excluded

- `ORKIO_CORE_RC1_EPIC002C_R2_IMPORT_HYGIENE_TARGET_APPLIER_LOCKED.zip`
  - selected over C/C-R1 because R2 removed corrupt patch and used official applier

- `ORKIO_CORE_RC1_EPIC002D_R1_APP_CORE_IMPORT_HYGIENE_TARGET_LOCKED.zip`

- `ORKIO_CORE_RC1_EPIC002E_R2_SERVICES_IMPORT_HYGIENE_TARGET_LOCKED.zip`
  - selected over E-R1 because ADR map mismatch was corrected

- `ORKIO_CORE_RC1_EPIC002F_R1_CORE_CAPABILITY_IMPORT_HYGIENE_TARGET_LOCKED.zip`

## Excluded

- EPIC-002 initial package: superseded by 002A/002B.
- EPIC-002B non-R1: delimiter collision risk.
- EPIC-002B-R1 `app/config/*`: shim not allowed.
- EPIC-002C original: global audit impossible and pycache present.
- EPIC-002C-R1: corrupt patch.
- EPIC-002E-R1: P2 documentary mismatch.
