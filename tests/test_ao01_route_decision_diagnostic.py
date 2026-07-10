from __future__ import annotations

from runtime.orkio_stream_precedence import build_chat_stream_precedence_payload


def test_route_diagnostics_are_attached_for_handled_decision() -> None:
    payload = build_chat_stream_precedence_payload(
        "Quais são os três principais riscos de uma empresa SaaS B2B?"
    )
    diag = payload["_ao01_route_diagnostics"]

    assert payload["handled"] is True
    assert diag["diagnostic_version"] == "AO01_ROUTE_DECISION_DIAGNOSTIC_V1"
    assert diag["guard_source_file"].endswith("orkio_executive_guard.py")
    assert len(diag["guard_source_sha256"]) == 64
    assert diag["guard_function"] == "eos06_build_router_precedence_payload"
    assert diag["handled"] is True


def test_route_diagnostics_are_attached_for_fail_open_decision() -> None:
    payload = build_chat_stream_precedence_payload(
        "Olá. Explique brevemente o que você faz."
    )
    diag = payload["_ao01_route_diagnostics"]

    assert payload["handled"] is False
    assert diag["diagnostic_version"] == "AO01_ROUTE_DECISION_DIAGNOSTIC_V1"
    assert diag["guard_source_file"].endswith("orkio_executive_guard.py")
    assert len(diag["guard_source_sha256"]) == 64
    assert diag["handled"] is False
