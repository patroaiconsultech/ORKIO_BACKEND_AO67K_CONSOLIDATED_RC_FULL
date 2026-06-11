from __future__ import annotations

"""
AO67B — Orkio Decision Mesh

Contrato:
- Especialistas internos podem gerar sinais.
- Orkio decide.
- Orkio responde.
- Nenhum agente interno vira speaker público.

Este módulo é uma camada de decisão/síntese. Ele não faz deploy, não escreve no
banco e não chama APIs externas. A integração com /api/chat/stream deve ocorrer
em fase posterior, após auditoria.
"""

import os
from typing import Any, Dict, Optional

from .hook_registry import (
    HOOK_REGISTRY_VERSION,
    hook_runtime_hints,
    public_hook_summary,
)
from .journey_memory import build_journey_memory_snapshot, journey_memory_runtime_hints
from .journey_router import JOURNEY_ROUTER_VERSION, route_public_journey, route_runtime_hints

try:
    from app.services.agent_access_policy import (
        AGENT_ACCESS_POLICY_VERSION,
        public_agent_access_denied_answer,
        public_agent_catalog_answer,
        is_public_agent_catalog_question,
        is_public_internal_agent_request,
    )
except Exception:  # pragma: no cover - defensive for partial overlays
    AGENT_ACCESS_POLICY_VERSION = "unavailable"

    def public_agent_access_denied_answer(*args: Any, **kwargs: Any) -> str:
        return (
            "Neste beta público, o Orkio conduz a experiência principal. "
            "Funcionalidades e agentes especializados poderão ser liberados futuramente conforme a evolução da conversa."
        )

    def public_agent_catalog_answer(*args: Any, **kwargs: Any) -> str:
        return (
            "Neste beta público, o Orkio é o condutor visível da experiência. "
            "Novas funcionalidades e agentes especializados poderão ser liberados futuramente conforme o uso correto e as necessidades identificadas."
        )

    def is_public_agent_catalog_question(*args: Any, **kwargs: Any) -> bool:
        return False

    def is_public_internal_agent_request(*args: Any, **kwargs: Any) -> bool:
        return False

try:
    from .visibility_policy import (
        VISIBILITY_POLICY_VERSION,
        apply_public_visibility_payload,
        public_visibility_runtime_hints,
    )
except Exception:  # pragma: no cover
    VISIBILITY_POLICY_VERSION = "unavailable"

    def apply_public_visibility_payload(payload: Dict[str, Any], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        data = dict(payload or {})
        data.update({"agent_id": "orkio", "agent_name": "Orkio", "final_speaker": "Orkio", "visible_agent": "Orkio"})
        return data

    def public_visibility_runtime_hints(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"routing": {"visible_agent": "Orkio", "routing_source": "visibility_policy_unavailable"}}

try:
    from .amcham_public_journey_policy import (
        AMCHAM_PUBLIC_JOURNEY_POLICY_VERSION,
        build_amcham_public_journey_decision,
    )
except Exception:  # pragma: no cover
    AMCHAM_PUBLIC_JOURNEY_POLICY_VERSION = "unavailable"

    def build_amcham_public_journey_decision(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"handled": False, "reason": "amcham_policy_unavailable"}


try:
    from .public_orkio_policy import (
        ORKIO_POLICY_VERSION as PUBLIC_ORKIO_POLICY_VERSION,
        build_public_orkio_policy_decision,
    )
except Exception:  # pragma: no cover
    PUBLIC_ORKIO_POLICY_VERSION = "unavailable"

    def build_public_orkio_policy_decision(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"handled": False, "reason": "public_orkio_policy_unavailable"}


ORKIO_DECISION_MESH_VERSION = "AO68I_ORKIO_PREMIUM_CANON_FASTLANE_V1"


def _env_bool(name: str, default: bool = True) -> bool:
    raw = str(os.getenv(name, "true" if default else "false") or "").strip().lower()
    if raw in {"1", "true", "yes", "y", "on", "enabled", "enable"}:
        return True
    if raw in {"0", "false", "no", "n", "off", "disabled", "disable"}:
        return False
    return bool(default)


def is_orkio_decision_mesh_enabled() -> bool:
    return _env_bool("ORKIO_DECISION_MESH_ENABLED", True)


def _base_decision(
    *,
    handled: bool,
    reason: str,
    answer: str = "",
    route: Optional[Dict[str, Any]] = None,
    memory_snapshot: Optional[Dict[str, Any]] = None,
    selected_hooks: Optional[list[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    route = dict(route or {})
    memory_snapshot = dict(memory_snapshot or {})
    selected_hooks = list(selected_hooks or route.get("selected_hooks") or [])

    hints: Dict[str, Any] = {
        "decision_mesh": {
            "version": ORKIO_DECISION_MESH_VERSION,
            "handled": bool(handled),
            "reason": reason,
            "public_speaker": "Orkio",
            "specialists_visible": False,
            "rule": "internal_specialists_advise_orkio_decides_orkio_answers",
        }
    }
    hints.update(route_runtime_hints(route))
    hints.update(hook_runtime_hints(selected_hooks, reason=reason))
    hints.update(journey_memory_runtime_hints(memory_snapshot))
    hints.update(public_visibility_runtime_hints(reason=reason, route_family="decision_mesh"))

    return {
        "handled": bool(handled),
        "reason": reason,
        "agent_id": "orkio",
        "agent_name": "Orkio",
        "final_speaker": "Orkio",
        "visible_agent": "Orkio",
        "answer": str(answer or "").strip(),
        "service": "orkio_decision_mesh",
        "provider": "platform",
        "status": "done" if handled else "not_handled",
        "policy_version": ORKIO_DECISION_MESH_VERSION,
        "hook_registry_version": HOOK_REGISTRY_VERSION,
        "journey_router_version": JOURNEY_ROUTER_VERSION,
        "amcham_public_journey_policy_version": AMCHAM_PUBLIC_JOURNEY_POLICY_VERSION,
        "public_orkio_policy_version": PUBLIC_ORKIO_POLICY_VERSION,
        "agent_access_policy_version": AGENT_ACCESS_POLICY_VERSION,
        "visibility_policy_version": VISIBILITY_POLICY_VERSION,
        "route": route,
        "public_hook_summary": public_hook_summary(selected_hooks),
        "journey_memory_snapshot": memory_snapshot,
        "write_executed": False,
        "proposal_created": False,
        "dispatch_executed": False,
        "branch_created": False,
        "pr_created": False,
        "deploy_executed": False,
        "runtime_hints": hints,
    }


def _technical_governance_public_answer() -> str:
    return (
        "Neste beta público, o Orkio conduz a experiência principal pelo chat por texto. "
        "Posso organizar sua necessidade em diagnóstico, riscos e próximos passos, sem expor fluxos técnicos internos. "
        "Com a evolução das conversas e o uso correto da ferramenta, novas funcionalidades poderão ser liberadas futuramente."
    )


def _message_mentions_amcham(value: Any) -> bool:
    normalized = str(value or "").lower()
    # Local lightweight normalization without importing extra dependencies.
    for src, dst in (("ã", "a"), ("á", "a"), ("à", "a"), ("â", "a"), ("é", "e"), ("ê", "e"), ("í", "i"), ("ó", "o"), ("ô", "o"), ("ú", "u"), ("ç", "c")):
        normalized = normalized.replace(src, dst)
    return any(marker in normalized for marker in ("amcham", "associado amcham", "associados amcham", "amcham rs"))


def _patroai_identity_answer() -> str:
    return (
        "A Patroai Consultech é a empresa criadora, mantenedora e detentora da tecnologia Orkio. "
        "Sua atuação une inteligência artificial aplicada, agentes personalizados, diagnóstico consultivo, governança e clareza executiva "
        "para ajudar pessoas e empresas a transformar ideias, problemas e objetivos em próximos passos concretos.\n\n"
        "A Patroai nasce com uma visão de tecnologia com propósito: servir com responsabilidade, proteger a confiança do usuário, "
        "organizar conhecimento e ampliar a capacidade humana de decidir, criar e executar.\n\n"
        "Daniel Graebin é o founder e CEO da Patroai Consultech."
    )


def _amcham_identity_answer() -> str:
    return (
        "A Patroai Consultech é empresa membro da AMCHAM RS e tem como missão levar disrupção digital aos associados por meio da tecnologia Orkio, "
        "unindo IA aplicada, agentes personalizados, diagnóstico consultivo e governança.\n\n"
        "O Orkio pode ser testado pelo chat em situações reais: desenvolvimento profissional, mapeamento de skills, liderança, inovação dentro da empresa, "
        "projetos de IA, diagnóstico de ideias e criação de novos negócios."
    )


def _fallback_public_journey_answer(intent: str, memory_snapshot: Dict[str, Any], *, current_message: Any = None) -> str:
    # Identity answers must not be polluted by continuity snippets such as
    # "na última interação..." because these are institutional facts, not journey
    # continuation prompts.
    if intent == "institutional_amcham_patroai":
        if _message_mentions_amcham(current_message):
            return _amcham_identity_answer()
        return _patroai_identity_answer()

    continuity = str(memory_snapshot.get("continuity_prompt") or "").strip()
    if intent == "open_conversation":
        return (
            "Posso te conduzir por uma trilha simples. Você quer explorar desenvolvimento profissional, "
            "skills, networking, liderança, inovação, IA no trabalho ou um novo negócio?"
        )

    base = {
        "professional_development": "Vamos tratar isso como uma trilha de desenvolvimento profissional.",
        "skills_mapping": "Vamos mapear seus skills de forma prática.",
        "networking": "Vamos trabalhar seu networking com foco em objetivo, posicionamento e conexões certas.",
        "leadership": "Vamos organizar sua evolução em liderança e comunicação.",
        "internal_innovation": "Vamos estruturar essa iniciativa como uma trilha de inovação dentro da empresa.",
        "ai_project": "Vamos transformar a ideia de IA em um primeiro projeto claro e testável.",
        "entrepreneurship": "Vamos estruturar o novo negócio começando por problema, público e proposta de valor.",
        "business_or_project_diagnostic": "Vamos organizar o diagnóstico em contexto, risco, oportunidade e próximo passo.",
        "platform_exploration": "Posso te conduzir por uma exploração guiada da plataforma.",
    }.get(intent, "Posso organizar sua necessidade em uma trilha simples.")

    question = " Para começar, qual é o seu objetivo principal agora?"
    if continuity:
        return f"{base} {continuity}{question}"
    return f"{base}{question}"


def build_orkio_decision_mesh_decision(
    message: Any,
    *,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    dest_mode: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
    previous_messages: Optional[list[Any]] = None,
    prior_memory: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not is_orkio_decision_mesh_enabled():
        return {"handled": False, "reason": "orkio_decision_mesh_disabled"}

    route = route_public_journey(
        message,
        visible_agent=visible_agent,
        target_agent_slug=target_agent_slug,
        route_plan=route_plan,
        include_internal_hooks=True,
    )
    selected_hooks = list(route.get("selected_hooks") or [])
    memory_snapshot = build_journey_memory_snapshot(
        current_message=message,
        previous_messages=previous_messages,
        prior_memory=prior_memory,
    )

    intent = str(route.get("intent") or "open_conversation")

    if is_public_internal_agent_request(
        message,
        visible_agent=visible_agent,
        target_agent_slug=target_agent_slug,
        dest_mode=dest_mode,
        route_plan=route_plan,
    ) or intent == "internal_agent_request":
        return _base_decision(
            handled=True,
            reason="decision_mesh_internal_agent_public_block",
            answer=public_agent_access_denied_answer(message),
            route=route,
            memory_snapshot=memory_snapshot,
            selected_hooks=selected_hooks,
        )

    if is_public_agent_catalog_question(message) or intent == "agent_catalog_request":
        return _base_decision(
            handled=True,
            reason="decision_mesh_public_agent_catalog_guard",
            answer=public_agent_catalog_answer(message),
            route=route,
            memory_snapshot=memory_snapshot,
            selected_hooks=selected_hooks,
        )

    if intent == "technical_governance_request":
        return _base_decision(
            handled=True,
            reason="decision_mesh_technical_governance_public_block",
            answer=_technical_governance_public_answer(),
            route=route,
            memory_snapshot=memory_snapshot,
            selected_hooks=selected_hooks,
        )

    # AO68I: premium canon fast-lane.
    # Institutional Patroai/Orkio, site and WhatsApp questions must not fall into
    # the heavier public journey/runtime path. This prevents generic answers and
    # terminal-guard timeouts for simple commercial/public questions.
    public_orkio = build_public_orkio_policy_decision(
        message,
        visible_agent=visible_agent,
        target_agent_slug=target_agent_slug,
        dest_mode=dest_mode,
        route_plan=route_plan,
    )
    direct_reasons = {
        "public_human_contact_whatsapp",
        "public_official_site_and_contact",
        "public_amcham_on_demand",
        "public_patroai_identity",
        "public_orkio_platform_identity",
        "public_implementation_process",
        "public_orkio_factual_created_at",
    }
    if public_orkio.get("handled") and str(public_orkio.get("reason") or "") in direct_reasons:
        answer = str(public_orkio.get("answer") or "").strip()
        decision = _base_decision(
            handled=True,
            reason=f"decision_mesh_delegated_{public_orkio.get('reason')}",
            answer=answer,
            route=route,
            memory_snapshot=memory_snapshot,
            selected_hooks=selected_hooks,
        )
        decision["delegated_policy"] = "public_orkio_policy_module"
        decision["delegated_decision"] = {
            "reason": public_orkio.get("reason"),
            "policy_version": public_orkio.get("policy_version") or PUBLIC_ORKIO_POLICY_VERSION,
            "runtime_hints": public_orkio.get("runtime_hints"),
        }
        return decision

    amcham = build_amcham_public_journey_decision(
        message,
        visible_agent=visible_agent,
        target_agent_slug=target_agent_slug,
        dest_mode=dest_mode,
        route_plan=route_plan,
    )
    if amcham.get("handled"):
        answer = str(amcham.get("answer") or "").strip()
        decision = _base_decision(
            handled=True,
            reason=f"decision_mesh_delegated_{amcham.get('reason') or 'amcham_public_journey'}",
            answer=answer,
            route=route,
            memory_snapshot=memory_snapshot,
            selected_hooks=selected_hooks,
        )
        decision["delegated_policy"] = "amcham_public_journey_policy"
        decision["delegated_decision"] = {
            "reason": amcham.get("reason"),
            "public_intent": amcham.get("public_intent"),
            "policy_version": amcham.get("policy_version"),
        }
        return decision

    if route.get("should_answer_immediately"):
        return _base_decision(
            handled=True,
            reason=f"decision_mesh_public_journey_{intent}",
            answer=_fallback_public_journey_answer(intent, memory_snapshot, current_message=message),
            route=route,
            memory_snapshot=memory_snapshot,
            selected_hooks=selected_hooks,
        )

    return _base_decision(
        handled=False,
        reason="decision_mesh_no_public_journey_match",
        answer="",
        route=route,
        memory_snapshot=memory_snapshot,
        selected_hooks=selected_hooks,
    )


def build_orkio_decision_mesh_stream_payload(
    decision: Dict[str, Any],
    *,
    persisted: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    data = dict(persisted or {})
    final_text = str(decision.get("answer") or "").strip()

    data.update(
        {
            "ok": True,
            "answer": final_text,
            "message": final_text,
            "final_text": final_text,
            "content": final_text,
            "text": final_text,
            "agent_id": "orkio",
            "agent_name": "Orkio",
            "final_speaker": "Orkio",
            "visible_agent": "Orkio",
            "service": "orkio_decision_mesh",
            "provider": "platform",
            "status": "done",
            "runtime_hints": decision.get("runtime_hints") or {},
        }
    )

    return apply_public_visibility_payload(
        data,
        blocked_agent=None,
        reason=str(decision.get("reason") or "orkio_decision_mesh"),
    )
