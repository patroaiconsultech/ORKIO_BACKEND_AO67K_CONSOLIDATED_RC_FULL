from typing import Any, Dict, List

DEFAULT_CAPABILITIES = {
    "chat": {"status": "production", "description": "Chat textual com histórico e threads."},
    "streaming_sse": {"status": "production", "description": "Resposta via SSE quando o runtime está saudável."},
    "agents": {"status": "beta", "description": "Agentes e perfis especializados em evolução."},
    "voice_realtime": {"status": "beta", "description": "Voz/realtime depende de ambiente e configuração."},
    "knowledge_fabric": {"status": "roadmap", "description": "Conhecimento governado com inventário e canonização."},
    "autonomous_deploy": {"status": "proposal", "description": "Autoevolução exige proposta e aprovação humana."},
}

def get_registry(registry: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return registry or DEFAULT_CAPABILITIES

def summarize_capabilities(registry: Dict[str, Any] | None = None) -> str:
    data = get_registry(registry)
    buckets: Dict[str, List[str]] = {}
    for cap_id, cap in data.items():
        status = str(cap.get("status", "unknown"))
        buckets.setdefault(status, []).append(f"- {cap_id}: {cap.get('description', '')}")
    order = ["production", "beta", "roadmap", "proposal", "unknown"]
    parts = []
    for status in order:
        if status in buckets:
            parts.append(f"{status.upper()}\n" + "\n".join(buckets[status]))
    return "\n\n".join(parts)

def resolve_capability(capability_id: str, registry: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = get_registry(registry)
    return data.get(capability_id, {"status": "unknown", "description": "Capacidade não registrada."})
