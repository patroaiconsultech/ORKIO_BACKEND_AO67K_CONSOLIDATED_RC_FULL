from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

@dataclass(frozen=True)
class SolutionPattern:
    pattern_id: str
    signature: str
    root_cause_family: str
    affected_domains: tuple[str, ...]
    required_tests: tuple[str, ...]
    common_risks: tuple[str, ...]
    confidence: float
    sample_size: int
    status: str = "active"

class PatternExtractor:
    def __init__(self, minimum_samples: int = 3) -> None:
        self.minimum_samples = minimum_samples

    def extract(self, outcomes: list[dict[str, Any]], *, root_cause_family: str) -> SolutionPattern | None:
        successful = [
            item for item in outcomes
            if item.get("payload", item).get("success") is True
            and not item.get("payload", item).get("regressions")
        ]
        if len(successful) < self.minimum_samples:
            return None
        payloads = [item.get("payload", item) for item in successful]
        domains = sorted({d for p in payloads for d in p.get("affected_domains", ())})
        tests = sorted({t for p in payloads for t in p.get("tests", ())})
        risks = sorted({r for p in payloads for r in p.get("risks", ())})
        signature_source = json.dumps(
            {"root": root_cause_family, "domains": domains, "tests": tests},
            sort_keys=True,
        )
        signature = sha256(signature_source.encode("utf-8")).hexdigest()
        confidence = min(0.95, 0.5 + 0.1 * len(successful))
        return SolutionPattern(
            pattern_id=f"pattern_{signature[:16]}",
            signature=signature,
            root_cause_family=root_cause_family,
            affected_domains=tuple(domains),
            required_tests=tuple(tests),
            common_risks=tuple(risks),
            confidence=confidence,
            sample_size=len(successful),
        )
