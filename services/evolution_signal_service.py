from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session


FORMULA_VERSION = "evolution_signals_backend_v1"
METRIC_KEYS = (
    "security_governance",
    "operational_reliability",
    "governed_autoevolution",
    "agent_knowledge",
    "core_modules",
    "evidence_observability",
    "premium_experience",
)

_SUCCESS_EXECUTION_STATUSES = {
    "completed",
    "dry_run_completed",
    "success",
    "succeeded",
    "passed",
}
_FAILURE_EXECUTION_STATUSES = {
    "failed",
    "error",
    "blocked",
    "cancelled",
    "canceled",
    "rolled_back",
}


@dataclass(frozen=True)
class TableState:
    agents: bool
    agent_knowledge: bool
    audit_logs: bool
    admin_proposals: bool
    admin_executions: bool
    evaluations: bool
    snapshots: bool


def _table_state(db: Session) -> TableState:
    bind = db.get_bind()
    inspector = inspect(bind)
    names = set(inspector.get_table_names())
    return TableState(
        agents="agents" in names,
        agent_knowledge="agent_knowledge" in names,
        audit_logs="audit_logs" in names,
        admin_proposals="admin_evolution_proposals" in names,
        admin_executions="admin_evolution_executions" in names,
        evaluations="agent_capability_evaluations" in names,
        snapshots="platform_evolution_metric_snapshots" in names,
    )


def _safe_json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    try:
        parsed = json.loads(str(value))
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return _boolish(raw)


def _score_from_checks(checks: Iterable[bool]) -> tuple[Optional[int], int]:
    values = list(checks)
    if not values:
        return None, 0
    passed = sum(1 for value in values if value)
    return round((passed / len(values)) * 100), len(values)


def _confidence(sample_count: int, *, base: int = 50, step: int = 4, cap: int = 95) -> int:
    if sample_count <= 0:
        return 0
    return min(cap, base + sample_count * step)


def _metric(
    *,
    key: str,
    label: str,
    score: Optional[int],
    confidence: int,
    sample_count: int,
    source: list[str],
    time_window: str,
    summary: str,
    missing_sources: Optional[list[str]] = None,
    estimated: bool = False,
) -> dict[str, Any]:
    missing = sorted(set(missing_sources or []))
    if score is None or sample_count <= 0:
        status = "source_unavailable" if missing else "insufficient_evidence"
        score = None
        confidence = 0
        sample_count = max(0, int(sample_count or 0))
    else:
        status = "estimated" if estimated else "measured"
        score = max(0, min(100, int(round(score))))
        confidence = max(0, min(100, int(round(confidence))))
    return {
        "key": key,
        "label": label,
        "score": score,
        "confidence": confidence,
        "sample_count": sample_count,
        "signal_status": status,
        "formula_version": FORMULA_VERSION,
        "source": source,
        "time_window": time_window,
        "missing_sources": missing,
        "summary": summary,
    }


def _query_agents(
    db: Session,
    tables: TableState,
    *,
    org_slug: str,
) -> list[dict[str, Any]]:
    if not tables.agents:
        return []
    rows = db.execute(
        text(
            """
            SELECT id, name, description, system_prompt, provider, model,
                   tool_policy, voice_id, avatar_url, strict_mode, rag_enabled
            FROM agents
            WHERE org_slug = :org_slug
            ORDER BY name ASC
            """
        ),
        {"org_slug": org_slug},
    ).mappings().all()
    return [dict(row) for row in rows]


def _query_agent_knowledge_counts(
    db: Session,
    tables: TableState,
    *,
    org_slug: str,
) -> dict[str, int]:
    if not tables.agent_knowledge:
        return {}
    rows = db.execute(
        text(
            """
            SELECT agent_id, COUNT(*) AS item_count
            FROM agent_knowledge
            WHERE org_slug = :org_slug AND enabled = TRUE
            GROUP BY agent_id
            """
        ),
        {"org_slug": org_slug},
    ).mappings().all()
    return {str(row["agent_id"]): int(row["item_count"] or 0) for row in rows}


def _query_evaluations(
    db: Session,
    tables: TableState,
    *,
    org_slug: str,
    cutoff: int,
) -> list[dict[str, Any]]:
    if not tables.evaluations:
        return []
    rows = db.execute(
        text(
            """
            SELECT agent_id, capability_id, status, score, confidence, created_at
            FROM agent_capability_evaluations
            WHERE org_slug = :org_slug AND created_at >= :cutoff
            ORDER BY created_at DESC
            """
        ),
        {"org_slug": org_slug, "cutoff": cutoff},
    ).mappings().all()
    return [dict(row) for row in rows]


def _query_admin_proposals(
    db: Session,
    tables: TableState,
    *,
    org_slug: str,
) -> list[dict[str, Any]]:
    if not tables.admin_proposals:
        return []
    rows = db.execute(
        text(
            """
            SELECT proposal_id, status, rollback_plan, checklist_json,
                   write_allowed, execution_allowed, human_approval_required
            FROM admin_evolution_proposals
            WHERE org_slug = :org_slug
            ORDER BY updated_at DESC
            LIMIT 500
            """
        ),
        {"org_slug": org_slug},
    ).mappings().all()
    return [dict(row) for row in rows]


def _query_admin_executions(
    db: Session,
    tables: TableState,
    *,
    org_slug: str,
    cutoff: int,
) -> list[dict[str, Any]]:
    if not tables.admin_executions:
        return []
    rows = db.execute(
        text(
            """
            SELECT execution_id, proposal_id, status, mode, result_json,
                   started_at, finished_at, created_at, updated_at
            FROM admin_evolution_executions
            WHERE org_slug = :org_slug AND created_at >= :cutoff
            ORDER BY created_at DESC
            LIMIT 1000
            """
        ),
        {"org_slug": org_slug, "cutoff": cutoff},
    ).mappings().all()
    return [dict(row) for row in rows]


def _query_audit_rows(
    db: Session,
    tables: TableState,
    *,
    org_slug: str,
    cutoff: int,
) -> list[dict[str, Any]]:
    if not tables.audit_logs:
        return []
    rows = db.execute(
        text(
            """
            SELECT request_id, path, status_code, latency_ms, action, created_at
            FROM audit_logs
            WHERE org_slug = :org_slug AND created_at >= :cutoff
            ORDER BY created_at DESC
            LIMIT 2000
            """
        ),
        {"org_slug": org_slug, "cutoff": cutoff},
    ).mappings().all()
    return [dict(row) for row in rows]


def _security_metric() -> dict[str, Any]:
    checks = [
        _env_flag("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", True),
        not _env_flag("ORKIO_ALLOW_AGENT_AUTO_WRITE", False),
        not _env_flag("ORKIO_ALLOW_AGENT_AUTO_DEPLOY", False),
        not _env_flag("EVOLUTION_ALLOW_DIRECT_SCHEMA", False),
        not _env_flag("EVOLUTION_ALLOW_CREATE_BRANCH", False),
        not _env_flag("EVOLUTION_ALLOW_WRITE_FILE", False),
        not _env_flag("EVOLUTION_ALLOW_CREATE_COMMIT", False),
        not _env_flag("EVOLUTION_ALLOW_OPEN_PR", False),
        not _env_flag("EVOLUTION_ALLOW_MERGE_PR", False),
        not _env_flag("EVOLUTION_ALLOW_DEPLOY", False),
        not _env_flag("EVOLUTION_ALLOW_ROLLBACK", False),
        _env_flag("ACCESS_GATE_SERVER_SIDE_ONLY", True),
    ]
    score, sample = _score_from_checks(checks)
    return _metric(
        key="security_governance",
        label="Segurança e governança",
        score=score,
        confidence=92,
        sample_count=sample,
        source=["runtime_control_flags"],
        time_window="current_runtime",
        summary="Controles fail-closed e flags de mutação avaliados sem expor valores.",
        estimated=True,
    )


def _autoevolution_metric(
    proposals: list[dict[str, Any]],
    executions: list[dict[str, Any]],
    *,
    missing: list[str],
) -> dict[str, Any]:
    checks: list[bool] = []
    for row in proposals:
        checks.extend(
            [
                _boolish(row.get("human_approval_required")),
                not _boolish(row.get("write_allowed")),
                not _boolish(row.get("execution_allowed")),
                bool(str(row.get("rollback_plan") or "").strip()),
                bool(_safe_json_list(row.get("checklist_json"))),
            ]
        )
    for row in executions:
        mode = str(row.get("mode") or "").strip().lower()
        checks.append("real" not in mode and "deploy" not in mode and "write" not in mode)
    score, sample = _score_from_checks(checks)
    return _metric(
        key="governed_autoevolution",
        label="Autoevolução governada",
        score=score,
        confidence=_confidence(len(proposals) + len(executions), base=58, step=3),
        sample_count=len(proposals) + len(executions),
        source=["admin_evolution_proposals", "admin_evolution_executions"],
        time_window="current_queue_and_30d_executions",
        missing_sources=missing,
        summary=f"{len(proposals)} proposta(s) e {len(executions)} execução(ões) governada(s) avaliadas.",
        estimated=True,
    )


def _reliability_metric(
    executions: list[dict[str, Any]],
    *,
    missing: list[str],
) -> dict[str, Any]:
    terminal = []
    success = 0
    failed = 0
    for row in executions:
        status = str(row.get("status") or "").strip().lower()
        if status in _SUCCESS_EXECUTION_STATUSES:
            terminal.append(row)
            success += 1
        elif status in _FAILURE_EXECUTION_STATUSES:
            terminal.append(row)
            failed += 1
    total = success + failed
    score = round((success / total) * 100) if total else None
    return _metric(
        key="operational_reliability",
        label="Confiabilidade operacional",
        score=score,
        confidence=_confidence(total, base=45, step=7),
        sample_count=total,
        source=["admin_evolution_executions"],
        time_window="30d",
        missing_sources=missing,
        summary=(
            f"{success} execução(ões) concluída(s), {failed} falha(s)."
            if total
            else "Sem amostra operacional terminal."
        ),
    )


def _evidence_metric(
    audits: list[dict[str, Any]],
    executions: list[dict[str, Any]],
    *,
    missing: list[str],
) -> dict[str, Any]:
    checks: list[bool] = []
    for row in audits:
        checks.extend(
            [
                bool(str(row.get("request_id") or "").strip()),
                bool(str(row.get("action") or row.get("path") or "").strip()),
                row.get("status_code") is not None,
                row.get("latency_ms") is not None,
            ]
        )
    for row in executions:
        checks.extend(
            [
                bool(str(row.get("execution_id") or "").strip()),
                bool(str(row.get("status") or "").strip()),
                row.get("created_at") is not None,
            ]
        )
    score, _ = _score_from_checks(checks)
    samples = len(audits) + len(executions)
    return _metric(
        key="evidence_observability",
        label="Evidência e observabilidade",
        score=score,
        confidence=_confidence(samples, base=50, step=2),
        sample_count=samples,
        source=["audit_logs", "admin_evolution_executions"],
        time_window="24h_audit_and_30d_executions",
        missing_sources=missing,
        summary=(
            f"{len(audits)} evento(s) de auditoria e {len(executions)} execução(ões) observada(s)."
            if samples
            else "Sem eventos de auditoria ou execuções observáveis na janela."
        ),
    )


def _agent_metrics(
    agents: list[dict[str, Any]],
    evaluations: list[dict[str, Any]],
    knowledge_counts: dict[str, int],
    *,
    evaluations_table_available: bool,
) -> list[dict[str, Any]]:
    by_agent: dict[str, list[dict[str, Any]]] = {}
    for row in evaluations:
        by_agent.setdefault(str(row.get("agent_id") or ""), []).append(row)

    result: list[dict[str, Any]] = []
    for agent in agents:
        agent_id = str(agent.get("id") or "")
        rows = by_agent.get(agent_id, [])
        passed = sum(1 for row in rows if str(row.get("status") or "").lower() == "passed")
        failed = sum(1 for row in rows if str(row.get("status") or "").lower() == "failed")
        if rows:
            weighted_total = 0.0
            weight_sum = 0.0
            capabilities = set()
            for row in rows:
                weight = max(1, int(row.get("confidence") or 0))
                weighted_total += int(row.get("score") or 0) * weight
                weight_sum += weight
                capabilities.add(str(row.get("capability_id") or ""))
            score = round(weighted_total / weight_sum) if weight_sum else None
            confidence = round(sum(int(row.get("confidence") or 0) for row in rows) / len(rows))
            status = "measured"
            missing_sources: list[str] = []
            capability_count = len(capabilities)
        else:
            score = None
            confidence = 0
            status = "insufficient_evidence" if evaluations_table_available else "source_unavailable"
            missing_sources = [] if evaluations_table_available else ["agent_capability_evaluations"]
            capability_count = 0

        result.append(
            {
                "agent_id": agent_id,
                "agent_name": str(agent.get("name") or agent_id),
                "score": score,
                "confidence": confidence,
                "sample_count": len(rows),
                "signal_status": status,
                "formula_version": FORMULA_VERSION,
                "capability_count": capability_count,
                "passed_count": passed,
                "failed_count": failed,
                "knowledge_items": int(knowledge_counts.get(agent_id, 0)),
                "missing_sources": missing_sources,
            }
        )
    return result


def _agent_knowledge_metric(
    agent_metrics: list[dict[str, Any]],
    *,
    missing: list[str],
) -> dict[str, Any]:
    measured = [row for row in agent_metrics if row.get("score") is not None]
    sample = sum(int(row.get("sample_count") or 0) for row in measured)
    if not measured or sample <= 0:
        score = None
        confidence = 0
    else:
        score = round(sum(int(row["score"]) * int(row["sample_count"]) for row in measured) / sample)
        confidence = round(sum(int(row["confidence"]) * int(row["sample_count"]) for row in measured) / sample)
    return _metric(
        key="agent_knowledge",
        label="Conhecimento dos agentes",
        score=score,
        confidence=confidence,
        sample_count=sample,
        source=["agent_capability_evaluations", "agent_knowledge"],
        time_window="90d",
        missing_sources=missing,
        summary=(
            f"{len(measured)} agente(s) com avaliação real e {sample} avaliação(ões)."
            if measured
            else "Agentes configurados, mas sem avaliações reais na janela."
        ),
    )


def _core_modules_metric(agents: list[dict[str, Any]], *, missing: list[str]) -> dict[str, Any]:
    checks: list[bool] = []
    for row in agents:
        checks.extend(
            [
                bool(str(row.get("name") or "").strip()),
                bool(str(row.get("system_prompt") or "").strip()),
                bool(str(row.get("model") or row.get("provider") or "").strip()),
                bool(str(row.get("tool_policy") or "").strip()),
            ]
        )
    score, _ = _score_from_checks(checks)
    return _metric(
        key="core_modules",
        label="Módulos principais",
        score=score,
        confidence=_confidence(len(agents), base=55, step=5),
        sample_count=len(agents),
        source=["agents"],
        time_window="current_configuration",
        missing_sources=missing,
        summary=f"{len(agents)} agente(s)/módulo(s) configurado(s) avaliados.",
        estimated=True,
    )


def _premium_experience_metric(agents: list[dict[str, Any]], *, missing: list[str]) -> dict[str, Any]:
    checks: list[bool] = []
    for row in agents:
        checks.extend(
            [
                bool(str(row.get("description") or "").strip()),
                bool(str(row.get("voice_id") or "").strip()),
                bool(str(row.get("avatar_url") or "").strip()),
                bool(str(row.get("model") or "").strip()),
            ]
        )
    score, _ = _score_from_checks(checks)
    return _metric(
        key="premium_experience",
        label="Experiência premium",
        score=score,
        confidence=_confidence(len(agents), base=50, step=5),
        sample_count=len(agents),
        source=["agents"],
        time_window="current_configuration",
        missing_sources=missing,
        summary="Completude de descrição, voz, avatar e modelo dos agentes configurados.",
        estimated=True,
    )


def build_current_snapshot(
    db: Session,
    *,
    org_slug: str,
    now_ts: int,
) -> dict[str, Any]:
    tables = _table_state(db)
    day_cutoff = now_ts - 86_400
    month_cutoff = now_ts - 30 * 86_400
    eval_cutoff = now_ts - 90 * 86_400

    agents = _query_agents(db, tables, org_slug=org_slug)
    knowledge_counts = _query_agent_knowledge_counts(db, tables, org_slug=org_slug)
    evaluations = _query_evaluations(db, tables, org_slug=org_slug, cutoff=eval_cutoff)
    proposals = _query_admin_proposals(db, tables, org_slug=org_slug)
    executions = _query_admin_executions(db, tables, org_slug=org_slug, cutoff=month_cutoff)
    audits = _query_audit_rows(db, tables, org_slug=org_slug, cutoff=day_cutoff)

    agents_missing = [] if tables.agents else ["agents"]
    eval_missing = [] if tables.evaluations else ["agent_capability_evaluations"]
    proposal_missing = [] if tables.admin_proposals else ["admin_evolution_proposals"]
    execution_missing = [] if tables.admin_executions else ["admin_evolution_executions"]
    audit_missing = [] if tables.audit_logs else ["audit_logs"]

    per_agent = _agent_metrics(
        agents,
        evaluations,
        knowledge_counts,
        evaluations_table_available=tables.evaluations,
    )

    metrics = [
        _security_metric(),
        _reliability_metric(executions, missing=execution_missing),
        _autoevolution_metric(
            proposals,
            executions,
            missing=proposal_missing + execution_missing,
        ),
        _agent_knowledge_metric(per_agent, missing=eval_missing),
        _core_modules_metric(agents, missing=agents_missing),
        _evidence_metric(
            audits,
            executions,
            missing=audit_missing + execution_missing,
        ),
        _premium_experience_metric(agents, missing=agents_missing),
    ]

    measured = [metric for metric in metrics if metric.get("score") is not None]
    total_weight = sum(max(1, int(metric.get("sample_count") or 0)) for metric in measured)
    if measured and total_weight > 0:
        overall_score = round(
            sum(int(metric["score"]) * max(1, int(metric.get("sample_count") or 0)) for metric in measured)
            / total_weight
        )
        overall_confidence = round(
            sum(
                int(metric.get("confidence") or 0)
                * max(1, int(metric.get("sample_count") or 0))
                for metric in measured
            )
            / total_weight
        )
    else:
        overall_score = None
        overall_confidence = 0

    return {
        "snapshot_kind": "current_readonly",
        "historical_trend": False,
        "formula_version": FORMULA_VERSION,
        "org_slug": org_slug,
        "generated_at": now_ts,
        "overall_score": overall_score,
        "overall_confidence": overall_confidence,
        "measured_metrics": len(measured),
        "total_metrics": len(METRIC_KEYS),
        "coverage_percent": round((len(measured) / len(METRIC_KEYS)) * 100),
        "metrics": metrics,
        "agents": per_agent,
        "write_executed": False,
    }


def capture_snapshot(
    db: Session,
    *,
    snapshot: dict[str, Any],
    snapshot_group_id: str,
    org_slug: str,
    actor_ref: str,
    reason: str,
    now_ts: int,
    id_factory,
) -> tuple[int, int]:
    metrics_persisted = 0
    agent_metrics_persisted = 0
    for metric in snapshot.get("metrics") or []:
        db.execute(
            text(
                """
                INSERT INTO platform_evolution_metric_snapshots (
                    snapshot_id, snapshot_group_id, org_slug, metric_key,
                    scope_type, scope_id, score, confidence, sample_count,
                    signal_status, formula_version, window_start, window_end,
                    source_json, missing_sources_json, evidence_refs_json,
                    captured_by, capture_reason, created_at
                ) VALUES (
                    :snapshot_id, :snapshot_group_id, :org_slug, :metric_key,
                    'platform', NULL, :score, :confidence, :sample_count,
                    :signal_status, :formula_version, :window_start, :window_end,
                    :source_json, :missing_sources_json, '[]',
                    :captured_by, :capture_reason, :created_at
                )
                """
            ),
            {
                "snapshot_id": id_factory(),
                "snapshot_group_id": snapshot_group_id,
                "org_slug": org_slug,
                "metric_key": metric["key"],
                "score": metric.get("score"),
                "confidence": metric.get("confidence", 0),
                "sample_count": metric.get("sample_count", 0),
                "signal_status": metric.get("signal_status", "insufficient_evidence"),
                "formula_version": snapshot.get("formula_version") or FORMULA_VERSION,
                "window_start": now_ts,
                "window_end": now_ts,
                "source_json": json.dumps(metric.get("source") or [], sort_keys=True),
                "missing_sources_json": json.dumps(metric.get("missing_sources") or [], sort_keys=True),
                "captured_by": actor_ref,
                "capture_reason": reason,
                "created_at": now_ts,
            },
        )
        metrics_persisted += 1

    for agent in snapshot.get("agents") or []:
        db.execute(
            text(
                """
                INSERT INTO platform_evolution_metric_snapshots (
                    snapshot_id, snapshot_group_id, org_slug, metric_key,
                    scope_type, scope_id, score, confidence, sample_count,
                    signal_status, formula_version, window_start, window_end,
                    source_json, missing_sources_json, evidence_refs_json,
                    captured_by, capture_reason, created_at
                ) VALUES (
                    :snapshot_id, :snapshot_group_id, :org_slug, 'agent_knowledge',
                    'agent', :scope_id, :score, :confidence, :sample_count,
                    :signal_status, :formula_version, :window_start, :window_end,
                    '["agent_capability_evaluations"]', :missing_sources_json, '[]',
                    :captured_by, :capture_reason, :created_at
                )
                """
            ),
            {
                "snapshot_id": id_factory(),
                "snapshot_group_id": snapshot_group_id,
                "org_slug": org_slug,
                "scope_id": agent["agent_id"],
                "score": agent.get("score"),
                "confidence": agent.get("confidence", 0),
                "sample_count": agent.get("sample_count", 0),
                "signal_status": agent.get("signal_status", "insufficient_evidence"),
                "formula_version": snapshot.get("formula_version") or FORMULA_VERSION,
                "window_start": now_ts,
                "window_end": now_ts,
                "missing_sources_json": json.dumps(agent.get("missing_sources") or [], sort_keys=True),
                "captured_by": actor_ref,
                "capture_reason": reason,
                "created_at": now_ts,
            },
        )
        agent_metrics_persisted += 1

    return metrics_persisted, agent_metrics_persisted


def list_history(
    db: Session,
    *,
    org_slug: str,
    cutoff: int,
    metric_key: Optional[str],
    scope_type: Optional[str],
    limit: int,
) -> list[dict[str, Any]]:
    tables = _table_state(db)
    if not tables.snapshots:
        return []
    clauses = ["org_slug = :org_slug", "created_at >= :cutoff"]
    params: dict[str, Any] = {
        "org_slug": org_slug,
        "cutoff": cutoff,
        "limit": limit,
    }
    if metric_key:
        clauses.append("metric_key = :metric_key")
        params["metric_key"] = metric_key
    if scope_type:
        clauses.append("scope_type = :scope_type")
        params["scope_type"] = scope_type
    rows = db.execute(
        text(
            f"""
            SELECT snapshot_id, metric_key, scope_type, scope_id, score,
                   confidence, sample_count, signal_status, formula_version,
                   window_start, window_end, created_at
            FROM platform_evolution_metric_snapshots
            WHERE {' AND '.join(clauses)}
            ORDER BY created_at ASC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()
    return [dict(row) for row in rows]
