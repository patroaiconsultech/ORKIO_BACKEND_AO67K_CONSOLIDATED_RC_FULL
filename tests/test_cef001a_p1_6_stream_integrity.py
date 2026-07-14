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


def test_stream_open_base_uses_locked_turn_owner_not_public_orkio() -> None:
    source = _main_source()
    base_start = source.index('base = {\n            "thread_id": tid_seed,')
    base_end = source.index("if glip_aria_mode:", base_start)
    base_block = source[base_start:base_end]

    assert '"agent_id": "aria" if glip_aria_mode else ao01_response_agent_id' in base_block
    assert '"agent_name": "Aria" if glip_aria_mode else ao01_response_agent_name' in base_block
    assert '"final_speaker": "Aria" if glip_aria_mode else ao01_response_agent_name' in base_block
    assert '"agent_id": "aria" if glip_aria_mode else "orkio"' not in base_block


def test_specialist_readonly_fastpath_uses_canonical_owner_for_orion_comma() -> None:
    source = _main_source()
    builder_start = source.index("def _build_specialist_readonly_audit_answer")
    builder_end = source.index("def _specialist_readonly_audit_fastpath_in_isolated_session", builder_start)
    builder_block = source[builder_start:builder_end]
    fastpath_end = source.index("def _ao20i_normalized_evolution_text", builder_end)
    fastpath_block = source[builder_end:fastpath_end]

    assert "requested_agent: str" in builder_block
    assert "_normalize_router_text(text)" not in builder_block
    assert "ao01_agent_turn_context" in fastpath_block
    assert "requested_agent=resolved_agent" in fastpath_block
    assert "raw.startswith(\"orion \")" not in fastpath_block
