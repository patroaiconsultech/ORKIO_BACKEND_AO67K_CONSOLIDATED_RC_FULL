from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping


REQUIRED_EXECUTION_EVIDENCE_FIELDS = (
    "tool_used",
    "tool_run_id",
    "repository",
    "branch",
    "commit",
    "operation",
    "result_digest",
    "started_at",
    "finished_at",
    "write_executed",
)


def has_verified_execution_evidence(receipt: Mapping[str, Any] | None) -> bool:
    payload = dict(receipt or {})
    for field in REQUIRED_EXECUTION_EVIDENCE_FIELDS:
        if field == "write_executed":
            if not isinstance(payload.get(field), bool):
                return False
            continue
        if not str(payload.get(field) or "").strip():
            return False
    return True


def normalize_execution_receipt(receipt: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = deepcopy(dict(receipt or {}))
    verified = has_verified_execution_evidence(payload)
    original_status = str(payload.get("status") or "").strip().lower()

    payload["evidence_verified"] = verified
    payload["verification_level"] = "tool_execution" if verified else "trace_lite"
    payload["execution_claim"] = "verified" if verified else "not_verified"

    if original_status == "executed" and not verified:
        payload["original_status"] = "executed"
        payload["status"] = "simulated"

    payload.setdefault("write_executed", False)
    return payload


def readonly_governance_fields() -> dict[str, bool]:
    return {
        "write_allowed": False,
        "proposal_created": False,
        "proposal_only": False,
        "commit_executed": False,
        "merge_executed": False,
        "deploy_executed": False,
        "migration_executed": False,
        "human_approval_required": True,
    }


def normalize_execution_receipts(receipts: Iterable[Mapping[str, Any] | None] | None) -> list[dict[str, Any]]:
    return [normalize_execution_receipt(item) for item in list(receipts or [])]


def execution_evidence_summary(receipts: Iterable[Mapping[str, Any] | None] | None) -> dict[str, Any]:
    normalized = normalize_execution_receipts(receipts)
    verified_count = sum(1 for item in normalized if bool(item.get("evidence_verified")))
    return {
        "receipts": normalized,
        "receipts_count": len(normalized),
        "verified_execution_count": verified_count,
        "has_verified_execution": verified_count > 0,
        "verification_level": "tool_execution" if verified_count > 0 else "trace_lite",
        "execution_claim": "verified" if verified_count > 0 else "not_verified",
    }


def _canonical_agent(value: Any) -> str:
    return str(value or "").strip().lower().replace("@", "").replace("-", "_").replace(" ", "_")


def has_verified_authorship_evidence(
    receipts: Iterable[Mapping[str, Any] | None] | None,
    *,
    target_agent: Any = None,
) -> bool:
    target = _canonical_agent(target_agent)
    if not target:
        return False
    for receipt in normalize_execution_receipts(receipts):
        if not bool(receipt.get("evidence_verified")):
            continue
        receipt_agent = _canonical_agent(
            receipt.get("authorship_agent")
            or receipt.get("response_author")
            or receipt.get("agent")
            or receipt.get("target_agent")
        )
        if receipt_agent == target and bool(
            receipt.get("authorship_verified")
            or receipt.get("specialist_response_verified")
            or receipt.get("specialist_invoked")
        ):
            return True
    return False


def non_executed_event_name(event: Any) -> str:
    value = str(event or "").strip()
    if not value:
        return "TRACE_LITE_NOT_VERIFIED"
    if value.endswith("_EXECUTED"):
        return value[: -len("_EXECUTED")] + "_TRACE_LITE"
    return value


TRACE_LITE_TECHNICAL_SUMMARY = (
    "Foi gerado um trace-lite de planejamento. Nenhuma ferramenta técnica teve "
    "acionamento comprovado."
)

TRACE_LITE_EXECUTIVE_DIAGNOSTIC = (
    "O Orion organizou uma análise preliminar baseada no contexto disponível; não há "
    "evidência de leitura de repositório, comando ou ferramenta acionada."
)

TRACE_LITE_CONFIRMED_EVIDENCE = (
    "Registrado: especialistas foram selecionados e registros de planejamento foram "
    "gerados. Operação técnica não verificada."
)

TRACE_LITE_FINAL_CONSOLIDATION = "Resultado preliminar, sem operação técnica comprovada."

TRACE_LITE_ARCHITECTURE_NOTES = [
    "Trace-lite indica planejamento preliminar, sem prova de ferramenta técnica.",
    "Especialistas selecionados não equivalem a leitura de repositório, comando ou execução técnica.",
    "Qualquer ação mutável permanece bloqueada até evidência real e aprovação humana explícita.",
]

TRACE_LITE_REMEDIATION_PLAN = [
    "1. Tratar esta resposta como análise preliminar.",
    "2. Coletar evidência real de ferramenta antes de declarar execução técnica.",
    "3. Manter escrita, PR, merge, migration e deploy bloqueados.",
]


TRACE_LITE_ASSESSMENT = (
    "Avaliacao preliminar em trace-lite. Nao ha prova de leitura, comando "
    "ou ferramenta tecnica acionada."
)

TRACE_LITE_TEXT_FIELDS = (
    "backend_assessment",
    "frontend_assessment",
    "integration_assessment",
    "main_risk",
    "executive_verdict",
    "principal_premium_blocker",
    "primary_product_adjustment",
    "primary_frontend_adjustment",
    "primary_backend_adjustment",
)

TRACE_LITE_SEQUENCE_FIELDS = (
    "recommended_actions",
    "suggested_actions",
    "risks",
    "root_causes",
    "next_actions",
    "findings",
    "risk_points",
    "premium_blockers",
    "top_improvements",
    "quick_wins_24h",
    "improvements_7d",
    "improvements_30d",
)

TRACE_LITE_CONTEXT_FIELDS = (
    "findings_by_specialty",
    "audit_plan",
    "executive_sections",
)

TRACE_LITE_PERSISTABLE_FIELDS = (
    "technical_summary",
    "executive_diagnostic",
    "backend_assessment",
    "frontend_assessment",
    "integration_assessment",
    "confirmed_evidence",
    "main_risk",
    "recommended_actions",
    "selected_specialists",
    "dispatch_receipts",
    "dispatch_receipts_appendix",
    "specialist_reports",
    "specialist_reports_appendix",
    "frontend_render_cards",
    "team_technical_audit",
    "final_consolidation",
)


def _mark_reports_as_trace_lite(value: Any) -> Any:
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, Mapping):
                marked = deepcopy(dict(item))
                template = marked.get("final_answer") or marked.get("message") or marked.get("findings")
                if template:
                    marked["planned_specialist_answer"] = template
                    marked["specialist_response_template"] = template
                marked["final_answer"] = "Template planejado pelo orquestrador; especialista nao invocado de forma comprovada."
                marked["findings"] = [
                    "Template planejado; sem prova de resposta real do especialista."
                ]
                marked["report_status"] = "simulated"
                marked["evidence_verified"] = False
                marked["verification_level"] = "trace_lite"
                marked["execution_claim"] = "not_verified"
                marked["specialist_invoked"] = False
                marked["specialist_response_verified"] = False
                marked["authorship_claim"] = "not_verified"
                out.append(marked)
            else:
                out.append(item)
        return out
    return value


def _trace_lite_sequence(label: str) -> list[str]:
    return [f"{label}: trace-lite preliminar; operacao tecnica nao verificada."]


CONCLUSIVE_STATUS_CLAIMS = {"executed", "completed", "success", "succeeded", "done"}
NON_CONCLUSIVE_STATUSES = {"ready", "planned", "blocked", "denied", "error", "cancelled", "canceled"}


def _normalized_status_without_evidence(status: Any, planned_status: str) -> tuple[str, bool]:
    current = str(status or "").strip().lower()
    if current in NON_CONCLUSIVE_STATUSES:
        return current, False
    if current in CONCLUSIVE_STATUS_CLAIMS:
        return (planned_status if planned_status in {"planned", "simulated"} else "simulated"), True
    return (planned_status if planned_status in {"planned", "simulated"} else "simulated"), bool(current)


def _is_single_target_envelope(envelope: Mapping[str, Any]) -> bool:
    mode = str(envelope.get("mode") or "").strip().lower()
    contract = str(envelope.get("response_contract") or "").strip().lower()
    selected = list(envelope.get("selected_specialists") or [])
    target = _canonical_agent(envelope.get("target_agent"))
    visible = _canonical_agent(envelope.get("visible_agent"))
    return bool(
        "single_target" in mode
        or contract == "specialist_direct_answer_v1"
        or (
            len(selected) == 1
            and target
            and target not in {"orion", "orkio"}
            and visible == target
        )
    )


def _apply_single_target_unverified_authorship(envelope: dict[str, Any], target_agent: Any) -> None:
    simulated_target = envelope.get("target_agent") or target_agent or "especialista"
    if simulated_target:
        envelope["simulated_target_agent"] = simulated_target
    envelope["simulated_final_speaker"] = envelope.get("final_speaker") or simulated_target
    envelope["visible_agent"] = "orion"
    envelope["final_speaker"] = "orion"
    envelope["authorship_status"] = "simulated_template_not_invoked"
    envelope["specialist_invocation_verified"] = False
    envelope["specialist_invoked"] = False
    envelope["specialist_response_verified"] = False
    envelope["authorship_claim"] = "not_verified"
    original_message = envelope.get("message")
    if original_message:
        envelope["planned_specialist_answer"] = original_message
        envelope["specialist_response_template"] = original_message
    envelope["message"] = (
        f"Orion gerou uma sugestao preliminar para o especialista {simulated_target}. "
        "O especialista nao foi comprovadamente invocado e esta resposta nao deve ser atribuida a ele."
    )
    envelope["response_contract"] = "trace_lite_preliminary_analysis_v1"


def _apply_general_trace_lite_authorship(envelope: dict[str, Any]) -> None:
    envelope["visible_agent"] = envelope.get("visible_agent") or "orion"
    envelope["final_speaker"] = envelope.get("final_speaker") or envelope.get("visible_agent") or "orion"
    envelope["authorship_status"] = "orchestrator_trace_lite_not_verified"
    envelope["specialist_invocation_verified"] = False
    envelope["specialist_invoked"] = False
    envelope["specialist_response_verified"] = False
    envelope["authorship_claim"] = "not_verified"
    envelope["message"] = (
        "Orion organizou uma analise preliminar em trace-lite. Nenhum especialista-alvo "
        "foi comprovadamente invocado."
    )
    envelope["response_contract"] = "trace_lite_general_preliminary_analysis_v1"


def apply_execution_evidence_to_envelope(
    payload: Mapping[str, Any] | None,
    *,
    receipts_key: str = "dispatch_receipts",
    planned_status: str = "simulated",
) -> dict[str, Any]:
    envelope = deepcopy(dict(payload or {}))
    summary = execution_evidence_summary(envelope.get(receipts_key) or [])
    target_agent = envelope.get("target_agent") or envelope.get("final_speaker") or envelope.get("visible_agent")
    single_target = _is_single_target_envelope(envelope)
    authorship_verified = has_verified_authorship_evidence(
        envelope.get(receipts_key) or [],
        target_agent=target_agent,
    )
    envelope[receipts_key] = summary["receipts"]
    envelope[f"{receipts_key}_count"] = summary["receipts_count"]
    envelope["verified_execution_count"] = summary["verified_execution_count"]
    envelope["execution_claim"] = summary["execution_claim"]
    envelope["verification_level"] = summary["verification_level"]
    envelope["dispatch_executed"] = bool(summary["has_verified_execution"])
    envelope["specialist_invoked"] = bool(authorship_verified)
    envelope["specialist_response_verified"] = bool(authorship_verified)
    envelope["authorship_claim"] = "verified" if authorship_verified else "not_verified"
    envelope["specialists_selected"] = bool(envelope.get("selected_specialists"))
    envelope["specialists_selected_count"] = len(list(envelope.get("selected_specialists") or []))

    if summary["has_verified_execution"] and authorship_verified:
        if target_agent:
            envelope["visible_agent"] = target_agent
            envelope["final_speaker"] = target_agent
        envelope["authorship_status"] = "verified_specialist_response"
    elif summary["has_verified_execution"] and not authorship_verified:
        if single_target:
            _apply_single_target_unverified_authorship(envelope, target_agent)
            envelope["authorship_status"] = "tool_execution_verified_authorship_not_verified"
        else:
            _apply_general_trace_lite_authorship(envelope)
            envelope["authorship_status"] = "tool_execution_verified_general_authorship_not_verified"
        return envelope

    if not summary["has_verified_execution"]:
        current_status = str(envelope.get("status") or "").strip().lower()
        if current_status == "executed":
            envelope["original_status"] = "executed"
        if current_status == "planned":
            envelope["status"] = "planned"
        else:
            envelope["status"] = planned_status if planned_status in {"planned", "simulated"} else "simulated"
        envelope["event"] = non_executed_event_name(envelope.get("event"))
        normalized_status, downgraded = _normalized_status_without_evidence(current_status, planned_status)
        envelope["status"] = normalized_status
        if downgraded:
            envelope["original_status"] = current_status or None
        envelope["execution_depth"] = "trace_lite"
        envelope["auditability_status"] = "trace_lite_not_verified"
        envelope["technical_summary"] = TRACE_LITE_TECHNICAL_SUMMARY
        envelope["executive_diagnostic"] = TRACE_LITE_EXECUTIVE_DIAGNOSTIC
        envelope["confirmed_evidence"] = TRACE_LITE_CONFIRMED_EVIDENCE
        envelope["final_consolidation"] = TRACE_LITE_FINAL_CONSOLIDATION
        envelope["architecture_notes"] = list(TRACE_LITE_ARCHITECTURE_NOTES)
        envelope["remediation_plan"] = list(TRACE_LITE_REMEDIATION_PLAN)
        for field in TRACE_LITE_TEXT_FIELDS:
            if field in envelope:
                envelope[field] = TRACE_LITE_ASSESSMENT
        for field in TRACE_LITE_SEQUENCE_FIELDS:
            if field in envelope:
                envelope[field] = _trace_lite_sequence(field)
        for field in TRACE_LITE_CONTEXT_FIELDS:
            if field in envelope:
                envelope[field] = {
                    "status": "trace_lite_not_verified",
                    "summary": TRACE_LITE_ASSESSMENT,
                }
        envelope["persistable_sections"] = list(TRACE_LITE_PERSISTABLE_FIELDS)
        envelope["source_audit_event"] = non_executed_event_name(envelope.get("source_audit_event"))
        if envelope.get("target_agent"):
            envelope["simulated_target_agent"] = envelope.get("target_agent")
        elif target_agent:
            envelope["simulated_target_agent"] = target_agent
        if envelope.get("final_speaker"):
            envelope["simulated_final_speaker"] = envelope.get("final_speaker")
        elif target_agent:
            envelope["simulated_final_speaker"] = target_agent
        envelope["final_speaker"] = "orion"
        envelope["visible_agent"] = "orion"
        envelope["authorship_status"] = "simulated_template_not_invoked"
        envelope["specialist_invocation_verified"] = False
        envelope["specialist_invoked"] = False
        envelope["specialist_response_verified"] = False
        envelope["authorship_claim"] = "not_verified"
        simulated_target = envelope.get("simulated_target_agent") or envelope.get("target_agent") or "especialista"
        original_message = envelope.get("message")
        if original_message:
            envelope["planned_specialist_answer"] = original_message
            envelope["specialist_response_template"] = original_message
        envelope["message"] = (
            f"Orion gerou uma sugestao preliminar para o especialista {simulated_target}. "
            "O especialista nao foi comprovadamente invocado e esta resposta nao deve ser atribuida a ele."
        )
        envelope["response_contract"] = "trace_lite_preliminary_analysis_v1"
        if not single_target:
            envelope.pop("simulated_target_agent", None)
            envelope.pop("simulated_final_speaker", None)
            envelope.pop("planned_specialist_answer", None)
            envelope.pop("specialist_response_template", None)
            _apply_general_trace_lite_authorship(envelope)
        envelope["specialist_reports"] = _mark_reports_as_trace_lite(envelope.get("specialist_reports"))
        envelope["specialist_reports_appendix"] = _mark_reports_as_trace_lite(envelope.get("specialist_reports_appendix"))
        envelope["frontend_render_cards"] = _mark_reports_as_trace_lite(envelope.get("frontend_render_cards"))
    return envelope


def build_trace_lite_receipt(
    *,
    agent: str,
    mode: str,
    scope: str,
    deliverable: str,
    generated_at: Any,
) -> dict[str, Any]:
    return normalize_execution_receipt(
        {
            "agent": str(agent or "").strip(),
            "status": "simulated",
            "mode": str(mode or "").strip(),
            "scope": str(scope or "").strip(),
            "deliverable": str(deliverable or "").strip(),
            "generated_at": generated_at,
            "tool_used": None,
            "tool_run_id": None,
            "repository": None,
            "branch": None,
            "commit": None,
            "operation": "specialist_analysis_template",
            "result_digest": None,
            "started_at": None,
            "finished_at": None,
            "write_executed": False,
        }
    )
