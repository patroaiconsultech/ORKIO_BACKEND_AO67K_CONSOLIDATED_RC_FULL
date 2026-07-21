# Cumulative scope: R1.4 → R1.6

## R1.5 foundation included

The cumulative delta includes the complete R1.5 foundation:

- tenant-isolated evolution objectives;
- KPI targets;
- formal KPI registry;
- multidimensional health scoring;
- missing-dimension and blocker handling;
- evidence-based diagnostics;
- transparent prioritization;
- proposal-only previews;
- controlled health snapshots;
- administrative audit;
- migration `0039_patch_evolution_intelligence_foundation`.

## R1.6 premium hardening

R1.6 adds:

- explicit runtime governance identity and consistency status;
- KPI collector and source provenance versions;
- exact collection window and sample metadata;
- immutable snapshots and immutable provenance;
- append-only snapshot invalidation events;
- versioned KPI target history;
- mandatory `change_reason` and `approval_id`;
- explicit `health_coverage`, `unknown_kpis`, `stale_kpis` and `blockers`;
- migration `0040_patch_evolution_intelligence_premium_lineage`.

## Out of scope

This release does not:

- enable autonomous code changes;
- enable auto-apply;
- commit, merge or deploy;
- modify chat ownership or SSE contracts;
- change auth behavior;
- implement frontend screens;
- claim production validation.
