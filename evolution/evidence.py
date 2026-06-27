from __future__ import annotations

from typing import Any, Iterable, List

from .models import Evidence

OEP_001_EVIDENCE_ENGINE_VERSION = "OEP_001_EVIDENCE_ENGINE_V1"

class EvidenceEngine:
    def from_log_line(self, line: str, source: str = "log") -> Evidence:
        text = str(line or "")
        return Evidence(source=source, type="log", confidence=0.75 if "PATCH_" in text or "trace_id" in text else 0.45, payload={"message": text}, tags=self._tags_from_text(text))

    def from_user_feedback(self, message: str, source: str = "user") -> Evidence:
        text = str(message or "").strip()
        return Evidence(source=source, type="user_feedback", confidence=0.8 if text else 0.2, payload={"message": text}, tags=self._tags_from_text(text))

    def from_metric(self, name: str, value: Any, source: str = "metric") -> Evidence:
        return Evidence(source=source, type="metric", confidence=0.7, payload={"name": name, "value": value}, tags=[str(name).lower()])

    def batch_from_logs(self, lines: Iterable[str], source: str = "log") -> List[Evidence]:
        return [self.from_log_line(line, source=source) for line in lines]

    def _tags_from_text(self, text: str) -> List[str]:
        lower = text.lower()
        tags = [tag for tag in ["frontend", "backend", "realtime", "team", "router", "deploy", "sse", "voice", "appconsole"] if tag in lower]
        return sorted(set(tags))
