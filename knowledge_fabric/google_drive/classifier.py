from __future__ import annotations

import re
from .models import DriveInventoryItem, ClassificationResult


_PERSONAL_HINTS = [
    "pessoal", "saúde", "saude", "família", "familia", "numerológico",
    "numerologico", "mapa numerologico", "privado", "diário", "diario",
]
_TECH_HINTS = [
    "backend", "frontend", "api", "runtime", "deploy", "arquitetura",
    "architecture", "sse", "stream", "python", "docker", "main.py",
]
_BUSINESS_HINTS = [
    "business plan", "bp_", "master plan", "holding", "fintegra",
    "valuation", "pitch", "go-to-market", "gtm",
]
_GOV_HINTS = [
    "governança", "governance", "auditoria", "proposal", "approval",
    "rollback", "adr", "constitution",
]
_ROADMAP_HINTS = [
    "roadmap", "plano", "release", "rc-", "rc_", "evolução", "evolucao",
]
_PRODUCT_HINTS = [
    "produto", "product", "ux", "onboarding", "avatar", "landing", "pwa",
]


def _contains_any(text: str, hints: list[str]) -> bool:
    normalized = text.lower()
    return any(h in normalized for h in hints)


def classify_drive_item(item: DriveInventoryItem) -> ClassificationResult:
    """Classify metadata only. Does not read file contents."""
    name = item.name or ""
    mime = item.mime_type or ""
    haystack = f"{name} {mime}".lower()

    if _contains_any(haystack, _PERSONAL_HINTS):
        return ClassificationResult(
            drive_file_id=item.drive_file_id,
            knowledge_class="personal",
            sensitivity="personal",
            status="blocked_pending_owner_review",
            confidence=0.72,
            reason="Filename suggests personal or founder-private content.",
        )

    if _contains_any(haystack, _TECH_HINTS):
        return ClassificationResult(
            drive_file_id=item.drive_file_id,
            knowledge_class="technical",
            sensitivity="internal",
            status="review_required",
            confidence=0.68,
            reason="Filename suggests technical/platform material.",
        )

    if _contains_any(haystack, _BUSINESS_HINTS):
        return ClassificationResult(
            drive_file_id=item.drive_file_id,
            knowledge_class="business_plan",
            sensitivity="confidential",
            status="review_required",
            confidence=0.68,
            reason="Filename suggests strategic/business material.",
        )

    if _contains_any(haystack, _GOV_HINTS):
        return ClassificationResult(
            drive_file_id=item.drive_file_id,
            knowledge_class="governance",
            sensitivity="internal",
            status="review_required",
            confidence=0.65,
            reason="Filename suggests governance/audit material.",
        )

    if _contains_any(haystack, _ROADMAP_HINTS):
        return ClassificationResult(
            drive_file_id=item.drive_file_id,
            knowledge_class="roadmap",
            sensitivity="internal",
            status="review_required",
            confidence=0.60,
            reason="Filename suggests roadmap or planning material.",
        )

    if _contains_any(haystack, _PRODUCT_HINTS):
        return ClassificationResult(
            drive_file_id=item.drive_file_id,
            knowledge_class="product",
            sensitivity="internal",
            status="review_required",
            confidence=0.60,
            reason="Filename suggests product/UX material.",
        )

    return ClassificationResult(
        drive_file_id=item.drive_file_id,
        knowledge_class="unknown",
        sensitivity="restricted",
        status="manual_review_required",
        confidence=0.35,
        reason="Metadata was insufficient for safe classification.",
    )
