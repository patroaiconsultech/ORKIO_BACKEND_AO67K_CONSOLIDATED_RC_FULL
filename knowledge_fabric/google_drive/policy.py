"""
Governed ingestion policy for Google Drive.

Hard rule:
- Google Drive is a source of raw knowledge, not a runtime source of truth.
- No document content may be used by Orkio until classified, reviewed and approved.
"""

DEFAULT_POLICY = {
    "mode": "inventory_only",
    "runtime_use_allowed": False,
    "requires_human_approval": True,
    "allowed_modes": [
        "inventory_only",
        "classification_only",
        "canon_candidate",
    ],
    "blocked_modes": [
        "direct_runtime_rag",
        "auto_canon",
        "auto_execute",
    ],
    "sensitivity_levels": [
        "public",
        "internal",
        "confidential",
        "restricted",
        "personal",
    ],
    "knowledge_classes": [
        "personal",
        "founder_memory",
        "institutional",
        "technical",
        "business_plan",
        "roadmap",
        "governance",
        "product",
        "legal",
        "finance",
        "archive",
        "unknown",
    ],
}


def enforce_policy(mode: str) -> None:
    """Raise ValueError if an unsafe mode is requested."""
    if mode in DEFAULT_POLICY["blocked_modes"]:
        raise ValueError(f"Unsafe Knowledge Fabric mode blocked: {mode}")
    if mode not in DEFAULT_POLICY["allowed_modes"]:
        raise ValueError(f"Unknown or unsupported Knowledge Fabric mode: {mode}")
