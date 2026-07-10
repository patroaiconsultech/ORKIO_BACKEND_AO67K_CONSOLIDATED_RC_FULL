from __future__ import annotations

"""MANUS UX R3.2 stream-entry integration adapter.

This file closes the pre-deploy integration gap identified after MANUS UX R3/R3.1:
R3's router guard must be invoked at the top of /api/chat/stream before legacy
financial calculators, public deterministic fastpaths, smart CTA decorators or
other runtime branches.

The module is intentionally pure and side-effect free.  It does not deploy,
commit, push, open PRs, read private sources, call external providers, write
databases, or mutate payloads in place.
"""

import copy
import hashlib
import inspect
import json
from typing import Any, Dict, Iterable, Iterator, List, Optional

try:
    from .orkio_executive_guard import ORKIO_EXECUTIVE_GUARD_VERSION, eos06_build_router_precedence_payload
except Exception:  # pragma: no cover - standalone test fallback
    from runtime.orkio_executive_guard import ORKIO_EXECUTIVE_GUARD_VERSION, eos06_build_router_precedence_payload

try:
    from .orkio_backend_cta_guard import enforce_backend_cta_policy
except Exception:  # pragma: no cover - standalone test fallback
    from runtime.orkio_backend_cta_guard import enforce_backend_cta_policy


MANUS_UX_R3_1_STREAM_INTEGRATION_VERSION = "AO01_SINGLE_ROUTE_AUTHORITY_STREAM_ADAPTER_V1"


_MESSAGE_KEYS = (
    "message",
    "user_message",
    "last_user_message",
    "prompt",
    "input",
    "query",
    "content",
    "text",
)


def extract_user_message_from_payload(payload_or_message: Any) -> str:
    """Best-effort extraction for common /api/chat/stream payload shapes."""

    if isinstance(payload_or_message, str):
        return payload_or_message

    if not isinstance(payload_or_message, dict):
        return str(payload_or_message or "")

    for key in _MESSAGE_KEYS:
        value = payload_or_message.get(key)
        if isinstance(value, str) and value.strip():
            return value

    nested_message = payload_or_message.get("message")
    if isinstance(nested_message, dict):
        content = nested_message.get("content") or nested_message.get("text")
        if isinstance(content, str) and content.strip():
            return content

    messages = payload_or_message.get("messages")
    if isinstance(messages, list):
        # Prefer the last explicit user message.
        for item in reversed(messages):
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or item.get("sender") or "").lower()
            content = item.get("content") or item.get("text") or item.get("message")
            if role == "user" and isinstance(content, str) and content.strip():
                return content
        # Fallback: last text-like message.
        for item in reversed(messages):
            if isinstance(item, dict):
                content = item.get("content") or item.get("text") or item.get("message")
                if isinstance(content, str) and content.strip():
                    return content

    return ""


def build_chat_stream_precedence_payload(payload_or_message: Any) -> Dict[str, Any]:
    """Build a terminal assistant payload when R3.1 should own the turn.

    Return {"handled": False, ...} when normal legacy runtime should continue.
    """

    user_message = extract_user_message_from_payload(payload_or_message)
    guard_payload = eos06_build_router_precedence_payload(user_message)

    if not guard_payload.get("handled"):
        category = str(guard_payload.get("category") or "not_eos06_precedence_case")
        force_full_llm_runtime = category == "full_llm_runtime_required"
        try:
            guard_source_file = inspect.getsourcefile(eos06_build_router_precedence_payload) or ""
            guard_source_sha256 = ""
            if guard_source_file:
                with open(guard_source_file, "rb") as source_file:
                    guard_source_sha256 = hashlib.sha256(source_file.read()).hexdigest()
        except Exception:
            guard_source_file = ""
            guard_source_sha256 = ""

        return {
            "handled": False,
            "category": category,
            "route_family": guard_payload.get("route_family") or "manus_ux_r3_1_stream_entry_precedence_gate",
            "guard_route_family": guard_payload.get("route_family"),
            "force_full_llm_runtime": force_full_llm_runtime,
            "block_executive_templates": force_full_llm_runtime,
            "block_public_deterministic_fastpaths": force_full_llm_runtime,
            "block_governed_evolution_fastpath": force_full_llm_runtime,
            "guard_payload": copy.deepcopy(guard_payload),
            "guard_version": ORKIO_EXECUTIVE_GUARD_VERSION,
            "guard_module": getattr(eos06_build_router_precedence_payload, "__module__", ""),
            "guard_function": getattr(eos06_build_router_precedence_payload, "__name__", ""),
            "guard_source_file": guard_source_file,
            "guard_source_sha256": guard_source_sha256,
            "stream_integration_version": MANUS_UX_R3_1_STREAM_INTEGRATION_VERSION,
            "commercial_cta_allowed": bool(guard_payload.get("commercial_cta_allowed", False)),
            "commercial_cta_suppressed": bool(guard_payload.get("commercial_cta_suppressed", True)),
        }

    payload = copy.deepcopy(guard_payload)
    answer = str(
        payload.get("answer")
        or payload.get("final_text")
        or payload.get("message")
        or payload.get("response_text")
        or ""
    )

    payload["answer"] = answer
    payload["message"] = answer
    payload["final_text"] = answer
    payload["response_text"] = answer
    payload["content"] = answer
    payload["text"] = answer
    payload["agent_id"] = payload.get("agent_id") or "orkio"
    payload["agent_name"] = payload.get("agent_name") or "Orkio"
    payload["done"] = True
    payload["stream_terminal"] = True
    payload["route_applied_at_stream_entry"] = True
    payload["stream_integration_version"] = MANUS_UX_R3_1_STREAM_INTEGRATION_VERSION

    runtime_hints = payload.setdefault("runtime_hints", {})
    routing = runtime_hints.setdefault("routing", {})
    routing.update(
        {
            "routing_source": routing.get("routing_source") or "MANUS_UX_R3_ROUTER_AND_CTA_GUARD_V1",
            "stream_entry_gate": MANUS_UX_R3_1_STREAM_INTEGRATION_VERSION,
            "route_applied_at_stream_entry": True,
            "block_legacy_financial_calculator": True,
            "block_public_deterministic_fastpaths": True,
            "block_default_commercial_cta": True,
            "execution_trace_priority": "secondary_collapsed",
        }
    )

    metadata = payload.setdefault("metadata", {})
    metadata.update(
        {
            "stream_entry_gate": MANUS_UX_R3_1_STREAM_INTEGRATION_VERSION,
            "route_applied_at_stream_entry": True,
            "routing": routing,
        }
    )

    sanitized, _changed = enforce_backend_cta_policy(payload)
    sanitized["handled"] = True
    sanitized["stream_terminal"] = True
    return sanitized


def _sse(event: str, data: Dict[str, Any]) -> str:
    return "event: " + event + "\n" + "data: " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n\n"


def iter_manus_ux_r3_1_sse_events(precedence_payload_or_request: Any) -> Iterator[str]:
    """Yield SSE events for FastAPI StreamingResponse.

    The input may be a previously built precedence payload or the original
    request payload.  If no precedence route applies, this iterator yields
    nothing; the caller should continue to the existing runtime instead.
    """

    if isinstance(precedence_payload_or_request, dict) and precedence_payload_or_request.get("route_applied_at_stream_entry"):
        payload = precedence_payload_or_request
    else:
        payload = build_chat_stream_precedence_payload(precedence_payload_or_request)

    if not payload.get("handled"):
        return

    routing = payload.get("runtime_hints", {}).get("routing", {})
    answer = str(payload.get("answer") or payload.get("final_text") or payload.get("message") or "")

    yield _sse(
        "status",
        {
            "phase": "router_precedence",
            "agent_id": payload.get("agent_id", "orkio"),
            "agent_name": payload.get("agent_name", "Orkio"),
            "category": payload.get("category"),
            "routing": routing,
        },
    )
    yield _sse(
        "chunk",
        {
            "delta": answer,
            "content": answer,
            "text": answer,
            "agent_id": payload.get("agent_id", "orkio"),
            "agent_name": payload.get("agent_name", "Orkio"),
            "metadata": payload.get("metadata", {}),
            "runtime_hints": payload.get("runtime_hints", {}),
        },
    )
    yield _sse(
        "agent_done",
        {
            "agent_id": payload.get("agent_id", "orkio"),
            "agent_name": payload.get("agent_name", "Orkio"),
            "category": payload.get("category"),
            "metadata": payload.get("metadata", {}),
            "runtime_hints": payload.get("runtime_hints", {}),
        },
    )
    yield _sse("done", payload)


def maybe_build_streaming_response_payload(payload_or_message: Any) -> Optional[Dict[str, Any]]:
    """Small helper for main.py: return terminal payload or None."""

    payload = build_chat_stream_precedence_payload(payload_or_message)
    if payload.get("handled"):
        return payload
    return None
