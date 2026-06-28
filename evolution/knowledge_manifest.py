from __future__ import annotations

KNOWLEDGE_MODULE_MANIFEST = {
    "oep": "003.1",
    "module": "knowledge_service_layer",
    "status": "proposal_only",
    "write_executed": False,
    "human_approval_required": True,
    "scope": [
        "backend",
        "evolution",
        "knowledge",
    ],
    "excluded_scope": [
        "chat",
        "chat_stream",
        "realtime",
        "voice",
        "team",
        "frontend",
    ],
    "tests": [
        "tests/oep003_1_knowledge_service_smoke.py",
    ],
}
