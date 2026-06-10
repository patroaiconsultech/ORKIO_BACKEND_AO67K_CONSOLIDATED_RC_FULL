# AO67F — Chat Stream Decision Gateway
# Destino real: app/runtime/chat_stream_decision_gateway.py
# Modo: PATCH_PREMIUM / minimal wiring-ready
#
# Objetivo:
# - Expor uma fachada única e auditável para /api/chat/stream.
# - Permitir que o main.py chame o Orkio Decision Mesh com wiring mínimo.
# - Manter Orkio como único speaker público.
# - Falhar aberto: se qualquer dependência modular quebrar, main.py segue fluxo atual.
# - Não chama LLM, não acessa rede e não executa escrita fora da memória opcional.
#
from __future__ import annotations

import os
from typing import Any, Dict, Iterable, Optional


CHAT_STREAM_DECISION_GATEWAY_VERSION = "AO67F_CHAT_STREAM_DECISION_GATEWAY_V2"
PUBLIC_SPEAKER = "Orkio"


def _env_bool(name: str, default: bool = True) -> bool:
    raw = str(os.getenv(name, "true" if default else "false") or "").strip().lower()
    if raw in {"1", "true", "yes", "y", "on", "enabled", "enable"}:
        return True
    if raw in {"0", "false", "no", "n", "off", "disabled", "disable"}:
        return False
    return bool(default)


def is_public_chat_gateway_enabled() -> bool:
    """Feature flag reversível para o AO67F.

    Default ligado para staging/ambiente paralelo.
    Em rollback lógico, usar:
      ORKIO_PUBLIC_CHAT_GATEWAY_ENABLED=false
    """
    return _env_bool("ORKIO_PUBLIC_CHAT_GATEWAY_ENABLED", True)


def is_journey_memory_commit_enabled(default: bool = False) -> bool:
    """Controle separado para persistência de memória.

    Default False no primeiro wiring para reduzir risco transacional.
    """
    return _env_bool("ORKIO_JOURNEY_MEMORY_COMMIT_ENABLED", default)


def _safe_str(value: Any, default: str = "") -> str:
    text = str(value if value is not None else default).strip()
    return text if text else default


def _extract_user_id(user: Any) -> Optional[str]:
    if user is None:
        return None
    if isinstance(user, dict):
        return str(user.get("id") or user.get("user_id") or user.get("sub") or "").strip() or None
    return str(
        getattr(user, "id", None)
        or getattr(user, "user_id", None)
        or getattr(user, "sub", None)
        or ""
    ).strip() or None


def _extract_org_slug(user: Any, explicit: Optional[str] = None) -> str:
    if explicit:
        return str(explicit or "public").strip() or "public"
    if isinstance(user, dict):
        return str(user.get("org_slug") or user.get("tenant") or user.get("org") or "public").strip() or "public"
    return str(
        getattr(user, "org_slug", None)
        or getattr(user, "tenant", None)
        or getattr(user, "org", None)
        or "public"
    ).strip() or "public"


def _load_prior_journey_memory(
    db: Any,
    *,
    org_slug: str,
    user_id: Optional[str],
    thread_id: Optional[str],
) -> Dict[str, Any]:
    try:
        from app.services.journey_memory_service import get_public_journey_context

        context = get_public_journey_context(
            db,
            org_slug=org_slug,
            user_id=user_id,
            thread_id=thread_id,
        )
        return dict(context.get("snapshot") or {})
    except Exception as exc:  # pragma: no cover - integração defensiva
        return {
            "version": "unavailable",
            "public_speaker": PUBLIC_SPEAKER,
            "error": "journey_memory_load_failed",
            "detail": str(exc)[:180],
        }


def _update_journey_memory_if_requested(
    db: Any,
    *,
    message: Any,
    org_slug: str,
    user_id: Optional[str],
    thread_id: Optional[str],
    commit_memory: bool,
) -> Dict[str, Any]:
    if db is None or not user_id:
        return {
            "ok": True,
            "persisted": False,
            "reason": "journey_memory_no_db_or_user",
            "public_speaker": PUBLIC_SPEAKER,
        }

    try:
        from app.services.journey_memory_service import update_public_journey_from_message

        return update_public_journey_from_message(
            db,
            message=message,
            org_slug=org_slug,
            user_id=user_id,
            thread_id=thread_id,
            commit=bool(commit_memory),
        )
    except Exception as exc:  # pragma: no cover - integração defensiva
        return {
            "ok": False,
            "persisted": False,
            "reason": "journey_memory_update_failed",
            "detail": str(exc)[:180],
            "public_speaker": PUBLIC_SPEAKER,
        }


def build_public_chat_gateway_decision(
    *,
    message: Any,
    db: Any = None,
    user: Any = None,
    org_slug: Optional[str] = None,
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    dest_mode: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
    previous_messages: Optional[Iterable[Any]] = None,
    commit_memory: Optional[bool] = None,
) -> Dict[str, Any]:
    """Decisão pública antes do RAG/OpenAI no corredor do chat.

    Retorno:
    - handled=True: main.py pode short-circuitar e responder via Orkio.
    - handled=False: main.py segue fluxo atual.

    Este gateway é fail-open. Em qualquer falha, retorna handled=False.
    """

    if not is_public_chat_gateway_enabled():
        return {
            "ok": True,
            "handled": False,
            "reason": "public_chat_gateway_disabled",
            "service": "chat_stream_decision_gateway",
            "version": CHAT_STREAM_DECISION_GATEWAY_VERSION,
            "agent_name": PUBLIC_SPEAKER,
            "final_speaker": PUBLIC_SPEAKER,
        }

    final_user_id = user_id or _extract_user_id(user)
    final_org_slug = _extract_org_slug(user, org_slug)
    final_thread_id = _safe_str(thread_id, "")
    should_commit_memory = (
        is_journey_memory_commit_enabled(default=False)
        if commit_memory is None
        else bool(commit_memory)
    )

    prior_memory = _load_prior_journey_memory(
        db,
        org_slug=final_org_slug,
        user_id=final_user_id,
        thread_id=final_thread_id,
    )

    try:
        from app.runtime.orkio_decision_mesh import build_orkio_decision_mesh_decision

        decision = build_orkio_decision_mesh_decision(
            message,
            visible_agent=visible_agent,
            target_agent_slug=target_agent_slug,
            dest_mode=dest_mode,
            route_plan=route_plan,
            previous_messages=list(previous_messages or []),
            prior_memory=prior_memory,
        )
    except Exception as exc:  # pragma: no cover - integração defensiva
        return {
            "ok": False,
            "handled": False,
            "reason": "decision_mesh_failed_open",
            "error": str(exc)[:240],
            "service": "chat_stream_decision_gateway",
            "version": CHAT_STREAM_DECISION_GATEWAY_VERSION,
            "agent_id": "orkio",
            "agent_name": PUBLIC_SPEAKER,
            "final_speaker": PUBLIC_SPEAKER,
            "visible_agent": PUBLIC_SPEAKER,
            "commit_memory": should_commit_memory,
        }

    memory_update = _update_journey_memory_if_requested(
        db,
        message=message,
        org_slug=final_org_slug,
        user_id=final_user_id,
        thread_id=final_thread_id,
        commit_memory=should_commit_memory,
    )

    handled = bool(decision.get("handled")) and bool(str(decision.get("answer") or "").strip())
    stream_payload: Dict[str, Any] = {}
    if handled:
        try:
            from app.runtime.orkio_decision_mesh import build_orkio_decision_mesh_stream_payload

            stream_payload = build_orkio_decision_mesh_stream_payload(decision)
        except Exception:
            answer = str(decision.get("answer") or "").strip()
            stream_payload = {
                "ok": True,
                "answer": answer,
                "message": answer,
                "content": answer,
                "final_text": answer,
                "text": answer,
                "agent_id": "orkio",
                "agent_name": PUBLIC_SPEAKER,
                "final_speaker": PUBLIC_SPEAKER,
                "visible_agent": PUBLIC_SPEAKER,
                "service": "chat_stream_decision_gateway",
                "provider": "platform",
                "status": "done",
            }

    return {
        "ok": True,
        "handled": handled,
        "reason": decision.get("reason") or "not_handled",
        "service": "chat_stream_decision_gateway",
        "version": CHAT_STREAM_DECISION_GATEWAY_VERSION,
        "agent_id": "orkio",
        "agent_name": PUBLIC_SPEAKER,
        "final_speaker": PUBLIC_SPEAKER,
        "visible_agent": PUBLIC_SPEAKER,
        "decision": decision,
        "stream_payload": stream_payload,
        "journey_memory_update": memory_update,
        "commit_memory": should_commit_memory,
        "integration_contract": {
            "insert_before": "AO66B_AMCHAM_PUBLIC_JOURNEY_FASTPATH_WIRE",
            "main_py_change_required": True,
            "specialists_visible": False,
            "rule": "internal_specialists_advise_orkio_decides_orkio_answers",
            "rollback_env": "ORKIO_PUBLIC_CHAT_GATEWAY_ENABLED=false",
        },
    }


def should_short_circuit_public_chat(gateway_decision: Dict[str, Any]) -> bool:
    return bool((gateway_decision or {}).get("handled")) and bool((gateway_decision or {}).get("stream_payload"))


def public_chat_gateway_runtime_hints(gateway_decision: Dict[str, Any]) -> Dict[str, Any]:
    decision = dict((gateway_decision or {}).get("decision") or {})
    return {
        "chat_stream_decision_gateway": {
            "version": CHAT_STREAM_DECISION_GATEWAY_VERSION,
            "handled": bool((gateway_decision or {}).get("handled")),
            "reason": (gateway_decision or {}).get("reason") or decision.get("reason") or "unknown",
            "public_speaker": PUBLIC_SPEAKER,
            "specialists_visible": False,
            "commit_memory": bool((gateway_decision or {}).get("commit_memory")),
            "rollback_env": "ORKIO_PUBLIC_CHAT_GATEWAY_ENABLED=false",
        }
    }


def build_public_chat_gateway_stream_payload(
    gateway_decision: Dict[str, Any],
    *,
    persisted: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Monta payload SSE final para o main.py.

    Mantém Orkio como speaker, injeta persisted e adiciona runtime_hints.
    """
    data = dict((gateway_decision or {}).get("stream_payload") or {})
    persisted_data = dict(persisted or {})

    final_text = str(
        data.get("answer")
        or data.get("message")
        or data.get("final_text")
        or data.get("content")
        or ""
    ).strip()

    data.update(persisted_data)
    data.update(
        {
            "ok": True,
            "answer": final_text,
            "message": final_text,
            "final_text": final_text,
            "content": final_text,
            "text": final_text,
            "agent_id": "orkio",
            "agent_name": PUBLIC_SPEAKER,
            "final_speaker": PUBLIC_SPEAKER,
            "visible_agent": PUBLIC_SPEAKER,
            "service": "chat_stream_decision_gateway",
            "provider": "platform",
            "status": "done",
        }
    )

    runtime_hints = data.get("runtime_hints") if isinstance(data.get("runtime_hints"), dict) else {}
    runtime_hints.update(public_chat_gateway_runtime_hints(gateway_decision))
    data["runtime_hints"] = runtime_hints

    return data
