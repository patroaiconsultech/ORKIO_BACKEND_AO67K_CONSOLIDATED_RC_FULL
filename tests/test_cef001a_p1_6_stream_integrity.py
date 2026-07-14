from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"


def _main_source() -> str:
    return MAIN.read_text(encoding="utf-8")


def test_internal_warroom_execution_fastpath_is_defined_before_use() -> None:
    source = _main_source()

    definition = source.find("def _internal_warroom_governed_execution_fastpath_in_isolated_session")
    call = source.find("asyncio.to_thread(_internal_warroom_governed_execution_fastpath_in_isolated_session")

    assert definition > 0
    assert call > 0
    assert definition < call


def test_public_fallbacks_are_blocked_for_locked_stream_owner() -> None:
    source = _main_source()
    guard = 'not bool(getattr(ao01_agent_turn_context, "ownership_locked", False))'

    assert re.search(
        rf"if _ao75_public_fastpath_allowed and not _ao01_force_full_llm_runtime and {re.escape(guard)}:",
        source,
    )
    assert re.search(
        rf"should_short_circuit_public_chat\(_ao67f_gateway_decision\)",
        source,
    )
    assert re.search(
        rf"and \(not bool\(getattr\(ao01_agent_turn_context, \"ownership_locked\", False\)\)\)\s+and isinstance\(_amcham_public_journey_decision, dict\)",
        source,
    )


def test_orion_readonly_negative_constraints_precede_execution_matcher() -> None:
    source = _main_source()
    matcher = source.index("def _is_internal_warroom_governed_execution_request")
    negative_call = source.index("if _orion_readonly_negative_constraints_active(text):", matcher)
    execution_markers = source.index("execution_markers = [", matcher)

    assert negative_call < execution_markers
    assert "is_readonly_technical_request(text)" in source
    assert "extract_mutation_constraints(text)" in source
    assert "sem proposta" in source
    assert "proposal_created=false" in source
