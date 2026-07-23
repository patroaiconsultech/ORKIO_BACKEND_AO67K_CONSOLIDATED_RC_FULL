from __future__ import annotations

from collections import Counter

from orion.contracts.models import Diagnosis, Evidence


class DiagnosisEngine:
    def diagnose(self, evidence: list[Evidence], context: object | None = None) -> Diagnosis:
        if not evidence:
            raise ValueError("evidence_required")
        parse_failures = [item for item in evidence if item.fact.startswith("python_parse_failure")]
        affected_files = sorted({item.source_ref for item in parse_failures})
        if parse_failures:
            cause = "python_source_parse_failure"
            confidence = 1.0
        else:
            cause = "no_deterministic_failure_detected"
            confidence = 0.55
        return Diagnosis(
            primary_root_cause=cause,
            evidence_ids=[item.evidence_id for item in evidence],
            confidence=confidence,
            affected_domains=["codebase"],
            affected_files=affected_files,
            secondary_causes=[],
            false_positives=[],
        )
