from __future__ import annotations


class ExtractiveSummarizer:
    """Very small deterministic summarizer for safe ingestion tests."""

    def summarize(self, text: str, max_chars: int = 600) -> str:
        normalized = " ".join(text.split())
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."
