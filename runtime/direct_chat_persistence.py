"""Direct-chat assistant persistence helper.

This module is intentionally dependency-injected so it can be imported safely
by the root-level ``main.py`` used in Railway deployments.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def persist_direct_assistant_message(
    *,
    db: Any,
    org: str,
    text: str,
    thread_id: str,
    Message: Any,
    select: Any,
    new_id: Any,
    now_ts: Any,
    logger: Any,
    trace_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    agent_name: Optional[str] = "Orkio",
) -> Dict[str, Any]:
    """Persist one assistant message for the direct-chat path.

    The function deliberately avoids content/time-window deduplication, because
    that can suppress valid responses from different turns. Transaction control
    stays local: commit on success, rollback and re-raise on failure.
    """
    final_text = str(text or "").strip()
    if not final_text:
        raise ValueError("direct_chat_persistence_empty_text")

    tid = str(thread_id or "").strip()
    if not tid:
        raise ValueError("direct_chat_persistence_missing_thread_id")

    message_id = str(new_id())
    message = Message(
        id=message_id,
        org_slug=str(org or "default"),
        thread_id=tid,
        role="assistant",
        content=final_text,
        agent_id=agent_id,
        agent_name=agent_name or "Orkio",
        created_at=int(now_ts()),
    )

    try:
        db.add(message)
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        try:
            logger.exception(
                "DIRECT_CHAT_ASSISTANT_PERSIST_FAILED trace_id=%s thread_id=%s",
                trace_id,
                tid,
            )
        except Exception:
            pass
        raise

    try:
        logger.info(
            "DIRECT_CHAT_ASSISTANT_PERSIST_OK trace_id=%s thread_id=%s assistant_message_id=%s",
            trace_id,
            tid,
            message_id,
        )
    except Exception:
        pass

    return {
        "assistant_message_id": message_id,
        "thread_id": tid,
        "persisted": True,
    }
