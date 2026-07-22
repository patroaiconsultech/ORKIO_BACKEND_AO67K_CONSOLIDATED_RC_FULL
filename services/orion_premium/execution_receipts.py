"""Auditable execution receipts. No receipt means no execution claim."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any


@dataclass(frozen=True)
class ExecutionReceipt:
    task_id: str
    tool_name: str
    started_at: str
    finished_at: str
    success: bool
    output_hash: str | None = None
    error_code: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_execution_receipt(
    *,
    task_id: str,
    tool_name: str,
    started_at: str,
    success: bool,
    output: Any = None,
    error_code: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ExecutionReceipt:
    output_hash = None
    if success:
        serialized = json.dumps(output, sort_keys=True, default=str)
        output_hash = sha256(serialized.encode("utf-8")).hexdigest()

    merged_metadata = dict(metadata or {})
    if output is not None:
        merged_metadata.setdefault("output", output)

    return ExecutionReceipt(
        task_id=task_id,
        tool_name=tool_name,
        started_at=started_at,
        finished_at=_utc_now(),
        success=bool(success),
        output_hash=output_hash,
        error_code=error_code,
        metadata=merged_metadata,
    )


def verify_execution_receipt(receipt: ExecutionReceipt) -> dict[str, Any]:
    failures: list[str] = []
    if not receipt.task_id:
        failures.append("task_id_missing")
    if not receipt.tool_name:
        failures.append("tool_name_missing")
    if not receipt.started_at or not receipt.finished_at:
        failures.append("timestamps_missing")
    if receipt.success and not receipt.output_hash:
        failures.append("output_hash_missing")
    if not receipt.success and not receipt.error_code:
        failures.append("error_code_missing")

    return {
        "verified": not failures,
        "failures": failures,
        "confidence": 1.0 if not failures else max(0.0, 1.0 - 0.2 * len(failures)),
    }
