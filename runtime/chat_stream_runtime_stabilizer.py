# P0-RS01 — Chat Stream Runtime Stabilizer
# Pure helper module for app/main.py.
# Scope: classify safe user-facing chat prompts that may bypass the heavy
# orchestration runtime during UAT stabilization, and compute sane stream
# guard timings without touching frontend, PWA, realtime, DB schema or deploy.

from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional


_GOVERNED_EXCLUSION_TERMS = (
    "patch",
    "diff",
    "commit",
    "pull request",
    "pr ",
    "github",
    "branch",
    "deploy",
    "rollback",
    "migration",
    "migrations",
    "schema",
    "database",
    "banco",
    "produção",
    "producao",
    "runtime audit",
    "auditoria técnica",
    "auditoria tecnica",
    "orchestration_audit",
    "proposal_only",
    "write_executed",
    "autoexecução",
    "autoexecucao",
    "self-evolution",
    "self evolution",
    "evolução governada",
    "evolucao governada",
    "terminal guard",
    "chat_stream_runtime_timeout",
    "/api/chat/stream",
    "api/chat/stream",
)

_USEFUL_CONVERSATION_HINTS = (
    "me explique",
    "explique",
    "crie",
    "faça",
    "faca",
    "monte",
    "organize",
    "resuma",
    "analise",
    "análise",
    "analise",
    "estratégia",
    "estrategia",
    "plano",
    "business plan",
    "relatório executivo",
    "relatorio executivo",
    "ideia",
    "diagnóstico",
    "diagnostico",
    "como",
    "qual",
    "quais",
    "por que",
    "porque",
    "o que",
    "vamos",
)

_AGENT_ALIASES = {
    "orkio": "orkio",
    "orion": "orion",
    "orion cto": "orion",
    "chris": "chris",
    "team": "team",
    "time": "team",
    "@team": "team",
    "@time": "team",
    "@orkio": "orkio",
    "@orion": "orion",
    "@chris": "chris",
}


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _lower(value: Any) -> str:
    return _norm(value).lower()


def _has_any(text: str, terms) -> bool:
    return any(term in text for term in terms)


def p0rs01_normalize_agent_slug(value: Any, *, default: str = "orkio") -> str:
    raw = _lower(value)
    raw = raw.strip().lstrip("@")
    raw = re.sub(r"\s+", " ", raw)
    if raw in _AGENT_ALIASES:
        return _AGENT_ALIASES[raw]
    if "orion" in raw:
        return "orion"
    if "chris" in raw:
        return "chris"
    if raw in {"team", "time"} or "team" in raw or "time" == raw:
        return "team"
    if "orkio" in raw:
        return "orkio"
    return default


def p0rs01_should_use_stream_lite(
    message: Any,
    *,
    visible_agent: Optional[str] = None,
    target_agent_slug: Optional[str] = None,
    dest_mode: Optional[str] = None,
    route_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return a conservative decision for the P0 stream-lite runtime.

    This bypass is intentionally user-facing only:
    - no GitHub/write/deploy/governance flows;
    - no migrations/schema/runtime audit;
    - no self-evolution/proposal-only paths;
    - preserves existing deterministic fast paths for very short greetings.
    """
    text = _norm(message)
    low = _lower(text)
    if not text:
        return {"handled": False, "reason": "empty_message"}

    if _has_any(low, _GOVERNED_EXCLUSION_TERMS):
        return {"handled": False, "reason": "governed_or_technical_exclusion"}

    visible = p0rs01_normalize_agent_slug(visible_agent, default="")
    target = p0rs01_normalize_agent_slug(target_agent_slug, default="")
    dest = _lower(dest_mode)
    route_plan = route_plan or {}

    explicit_team = bool(
        "@team" in low
        or "@time" in low
        or low.startswith("team ")
        or low.startswith("time ")
        or dest == "multi"
        or str(route_plan.get("route_family") or "").strip().lower() in {"team", "multi", "orchestration_team_lite"}
    )

    explicit_agent = None
    for token in ("@orion", "@chris", "@orkio"):
        if token in low:
            explicit_agent = token.lstrip("@")
            break
    if not explicit_agent:
        explicit_agent = target or visible or ""

    # Preserve tiny greeting/status fast-paths that already work.
    tiny = low in {"oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hello", "hi"}
    if tiny:
        return {"handled": False, "reason": "tiny_fastpath_preserved"}

    useful_natural = bool(len(text) >= 14 and _has_any(low, _USEFUL_CONVERSATION_HINTS))

    if explicit_team:
        return {
            "handled": True,
            "mode": "team_lite",
            "agent_slug": "orkio",
            "reason": "explicit_team_stream_lite",
        }

    if explicit_agent in {"orkio", "orion", "chris"}:
        return {
            "handled": True,
            "mode": "direct_agent_lite",
            "agent_slug": explicit_agent,
            "reason": "explicit_agent_stream_lite",
        }

    if useful_natural:
        return {
            "handled": True,
            "mode": "plain_useful_lite",
            "agent_slug": "orkio",
            "reason": "plain_useful_stream_lite",
        }

    return {"handled": False, "reason": "not_stream_lite_candidate"}


def p0rs01_effective_stream_timeout(
    env_timeout: Any,
    env_cap: Any,
    *,
    candidate: Optional[Dict[str, Any]] = None,
) -> int:
    """Compute a safe timeout floor for principal runtime UAT.

    The observed failure pattern was a ~16s terminal guard. The objective for
    user-facing useful prompts is 20-30s. This function does not uncap runtime;
    it enforces a minimum only where the stream is user-facing and keeps the cap
    bounded.
    """
    try:
        max_wait_s = int(str(env_timeout or "45").strip() or "45")
    except Exception:
        max_wait_s = 45

    try:
        max_cap_s = int(str(env_cap or "180").strip() or "180")
    except Exception:
        max_cap_s = 180

    max_cap_s = max(30, min(max_cap_s, 300))
    min_floor = 30
    if isinstance(candidate, dict) and candidate.get("handled"):
        min_floor = 35

    return max(min_floor, min(max_wait_s, max_cap_s))


def p0rs01_build_system_prompt(
    *,
    agent_name: str = "Orkio",
    mode: str = "plain_useful_lite",
    base_system_prompt: Optional[str] = None,
    executive_context_overlay: Optional[str] = None,
) -> str:
    safe_agent_name = _norm(agent_name) or "Orkio"
    base = _norm(base_system_prompt)

    if mode == "team_lite":
        role = (
            f"Você é {safe_agent_name}, coordenando uma resposta consolidada em modo leve. "
            "Responda como uma síntese executiva do time, sem afirmar que acionou ferramentas, deploys, escrita em GitHub ou execução real. "
            "Se houver múltiplas frentes, organize por diagnóstico, recomendação e próximo passo."
        )
    elif mode == "direct_agent_lite":
        role = (
            f"Você é {safe_agent_name}. Responda diretamente ao usuário como esse agente, de forma útil, clara e objetiva. "
            "Não afirme ter executado ações externas. Não invente logs, deploys, arquivos criados ou validações."
        )
    else:
        role = (
            f"Você é {safe_agent_name}. Responda de forma útil, premium e objetiva. "
            "Priorize clareza, próximos passos e utilidade prática. Não afirme execução real sem evidência."
        )

    guard = (
        "\n\nContrato de segurança operacional:\n"
        "- Não executar patch, deploy, commit, migration ou escrita externa.\n"
        "- Não criar proposal_id.\n"
        "- Se a pergunta exigir ação técnica real, entregue diagnóstico/proposta e marque validação pendente.\n"
        "- Responda em português do Brasil, salvo se o usuário pedir outro idioma.\n"
        "- Mantenha a resposta entre 6 e 14 parágrafos curtos."
    )

    prompt = f"{base.strip()}\n\n{role}{guard}" if base else f"{role}{guard}"
    if safe_agent_name.strip().lower().startswith("orkio"):
        try:
            from app.agents.orkio.advisor import append_orkio_advisor_overlay
        except Exception:
            try:
                from agents.orkio.advisor import append_orkio_advisor_overlay
            except Exception:
                append_orkio_advisor_overlay = None
        if append_orkio_advisor_overlay is not None:
            prompt = append_orkio_advisor_overlay(prompt)
    executive_overlay = _norm(executive_context_overlay)
    if executive_overlay and executive_overlay not in prompt:
        prompt = f"{prompt}\n\n{executive_overlay}".strip()
    return prompt


def p0rs01_build_provider_failure_text(*, agent_name: str = "Orkio", code: str = "", detail: str = "") -> str:
    safe_agent_name = _norm(agent_name) or "Orkio"
    safe_code = _norm(code) or "LLM_ERROR"
    safe_detail = _norm(detail)
    detail_line = f"\n\nDetalhe técnico resumido: {safe_detail[:260]}" if safe_detail else ""
    return (
        f"{safe_agent_name} recebeu sua solicitação, mas o provedor de IA não concluiu esta chamada com sucesso. "
        "A conversa foi preservada e o stream será encerrado com segurança.\n\n"
        f"Código: {safe_code}.{detail_line}\n\n"
        "Tente novamente em alguns instantes ou reformule em uma solicitação mais específica."
    )
