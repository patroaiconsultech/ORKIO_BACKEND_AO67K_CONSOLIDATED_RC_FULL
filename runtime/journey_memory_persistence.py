# AO67D — Journey Memory persistence
# Destino real: app/runtime/journey_memory_persistence.py
# Modo: PATCH_PREMIUM / foundation-only / no main.py wiring
#
# Usa tabelas existentes: runtime_memories e trial_events.
# Não cria migration, não altera schema, não executa escrita sem sessão explícita.
#
from __future__ import annotations

from typing import Any, Dict, Optional
from decimal import Decimal
import json
import time
import uuid

from .journey_memory import (
    JOURNEY_MEMORY_VERSION,
    PUBLIC_SPEAKER,
    JourneySignal,
    build_journey_continuity_hint,
    build_public_memory_receipt,
    merge_journey_snapshot,
)

JOURNEY_MEMORY_KEY = "orkio.public_journey.snapshot"
JOURNEY_EVENT_NAME = "orkio_public_journey_signal"


def _now_ts() -> int:
    return int(time.time())


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    except Exception:
        return "{}"


def _json_loads(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(str(value or "{}"))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _safe_confidence(value: Any) -> Decimal:
    try:
        numeric = max(0.0, min(1.0, float(value)))
    except Exception:
        numeric = 0.60
    return Decimal(str(round(numeric, 2)))


def load_public_journey_snapshot(
    db: Any,
    *,
    org_slug: str = "public",
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Carrega snapshot de jornada, com fallback seguro.

    Requer sessão SQLAlchemy explícita. Se db/model/tabela falhar, retorna {}.
    """

    if db is None or not user_id:
        return {}

    try:
        from app.models import RuntimeMemory

        query = (
            db.query(RuntimeMemory)
            .filter(RuntimeMemory.org_slug == str(org_slug or "public"))
            .filter(RuntimeMemory.user_id == str(user_id))
            .filter(RuntimeMemory.memory_key == JOURNEY_MEMORY_KEY)
            .order_by(RuntimeMemory.updated_at.desc())
        )

        if thread_id:
            # Preferir memória do thread atual, mas aceitar memória geral do usuário se não houver.
            thread_row = query.filter(RuntimeMemory.thread_id == str(thread_id)).first()
            if thread_row is not None:
                return _json_loads(thread_row.memory_value)

        row = query.first()
        return _json_loads(row.memory_value) if row is not None else {}
    except Exception:
        return {}


def save_public_journey_snapshot(
    db: Any,
    snapshot: Dict[str, Any],
    *,
    org_slug: str = "public",
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    source: str = "ao67d_journey_memory",
    confidence: float = 0.70,
    commit: bool = False,
) -> Dict[str, Any]:
    """Persiste snapshot em runtime_memories.

    commit=False por padrão para permitir uso dentro de transações existentes.
    """

    if db is None or not user_id:
        return {"ok": False, "reason": "missing_db_or_user", "snapshot": snapshot or {}}

    now = _now_ts()
    payload = dict(snapshot or {})
    payload["version"] = payload.get("version") or JOURNEY_MEMORY_VERSION
    payload["public_speaker"] = PUBLIC_SPEAKER
    payload["updated_at"] = payload.get("updated_at") or now

    try:
        from app.models import RuntimeMemory

        query = (
            db.query(RuntimeMemory)
            .filter(RuntimeMemory.org_slug == str(org_slug or "public"))
            .filter(RuntimeMemory.user_id == str(user_id))
            .filter(RuntimeMemory.memory_key == JOURNEY_MEMORY_KEY)
        )

        if thread_id:
            row = query.filter(RuntimeMemory.thread_id == str(thread_id)).first()
        else:
            row = query.filter(RuntimeMemory.thread_id.is_(None)).first()

        if row is None:
            row = RuntimeMemory(
                id=uuid.uuid4().hex,
                org_slug=str(org_slug or "public"),
                user_id=str(user_id),
                thread_id=str(thread_id) if thread_id else None,
                memory_key=JOURNEY_MEMORY_KEY,
                memory_value=_json_dumps(payload),
                source=source,
                confidence=_safe_confidence(confidence),
                created_at=now,
                updated_at=now,
            )
            db.add(row)
        else:
            row.memory_value = _json_dumps(payload)
            row.source = source
            row.confidence = _safe_confidence(confidence)
            row.updated_at = now

        if commit:
            db.commit()

        return {
            "ok": True,
            "memory_key": JOURNEY_MEMORY_KEY,
            "snapshot": payload,
            "receipt": build_public_memory_receipt(payload),
        }
    except Exception as exc:
        try:
            if commit:
                db.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "persistence_error", "error": str(exc), "snapshot": payload}


def record_public_journey_event(
    db: Any,
    signal: JourneySignal | Dict[str, Any],
    *,
    org_slug: str = "public",
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    commit: bool = False,
) -> Dict[str, Any]:
    """Registra evento leve em trial_events, se a tabela/model existir."""

    if db is None or not user_id:
        return {"ok": False, "reason": "missing_db_or_user"}

    payload = signal.to_dict() if isinstance(signal, JourneySignal) else dict(signal or {})
    payload["public_speaker"] = PUBLIC_SPEAKER
    payload["version"] = payload.get("version") or JOURNEY_MEMORY_VERSION

    try:
        from app.models import TrialEvent

        row = TrialEvent(
            id=uuid.uuid4().hex,
            org_slug=str(org_slug or "public"),
            user_id=str(user_id),
            thread_id=str(thread_id) if thread_id else None,
            event_name=JOURNEY_EVENT_NAME,
            payload_json=_json_dumps(payload),
            created_at=_now_ts(),
        )
        db.add(row)
        if commit:
            db.commit()
        return {"ok": True, "event_name": JOURNEY_EVENT_NAME}
    except Exception as exc:
        try:
            if commit:
                db.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "event_persistence_error", "error": str(exc)}


def update_public_journey_memory(
    db: Any,
    signal: JourneySignal | Dict[str, Any],
    *,
    org_slug: str = "public",
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    commit: bool = False,
) -> Dict[str, Any]:
    """Carrega, mescla, salva snapshot e tenta registrar evento.

    Esta é a função principal para integração futura.
    """

    previous = load_public_journey_snapshot(
        db,
        org_slug=org_slug,
        user_id=user_id,
        thread_id=thread_id,
    )
    snapshot = merge_journey_snapshot(previous, signal)

    save_result = save_public_journey_snapshot(
        db,
        snapshot,
        org_slug=org_slug,
        user_id=user_id,
        thread_id=thread_id,
        confidence=(signal.confidence if isinstance(signal, JourneySignal) else signal.get("confidence", 0.70)),
        commit=False,
    )
    event_result = record_public_journey_event(
        db,
        signal,
        org_slug=org_slug,
        user_id=user_id,
        thread_id=thread_id,
        commit=False,
    )

    if commit:
        try:
            db.commit()
        except Exception as exc:
            try:
                db.rollback()
            except Exception:
                pass
            return {"ok": False, "reason": "commit_failed", "error": str(exc), "snapshot": snapshot}

    return {
        "ok": bool(save_result.get("ok")),
        "snapshot": snapshot,
        "continuity_hint": build_journey_continuity_hint(snapshot),
        "save": save_result,
        "event": event_result,
    }


def build_journey_memory_context(
    db: Any,
    *,
    org_slug: str = "public",
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Contexto compacto para Decision Mesh / overlay futuro."""

    snapshot = load_public_journey_snapshot(
        db,
        org_slug=org_slug,
        user_id=user_id,
        thread_id=thread_id,
    )
    return {
        "version": JOURNEY_MEMORY_VERSION,
        "public_speaker": PUBLIC_SPEAKER,
        "snapshot": snapshot,
        "continuity_hint": build_journey_continuity_hint(snapshot),
        "receipt": build_public_memory_receipt(snapshot),
    }
