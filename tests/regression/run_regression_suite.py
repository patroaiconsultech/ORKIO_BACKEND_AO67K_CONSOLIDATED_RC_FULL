from __future__ import annotations

import subprocess
import sys
from pathlib import Path


TESTS = [
    "tests/oep003_knowledge_vault_smoke.py",
    "tests/oep003_1_knowledge_service_smoke.py",
    "tests/oep003_2_knowledge_manifest_governance_smoke.py",
    "tests/oep003_3_evolution_engine_compat_smoke.py",
    "tests/oep004_distiller_smoke.py",
    "tests/oep004_1_distiller_knowledge_bridge_smoke.py",
    "tests/oep004_2_batch_idempotency_smoke.py",
    "tests/oep004_3_conversation_intake_governance_smoke.py",
    "tests/oep005_proposal_engine_smoke.py",
    "tests/oep005_1_proposal_ranking_smoke.py",
    "tests/oep005_2_conflict_detection_smoke.py",
    "tests/oep005_3_approval_workflow_smoke.py",
    "tests/oep006_learning_engine_foundation_smoke.py",
    "tests/oep006_1_learning_memory_smoke.py",
    "tests/oep006_2_outcome_tracker_smoke.py",
    "tests/oep006_3_confidence_calibration_smoke.py",
    "tests/oep006_4_experience_repository_smoke.py",
    "tests/oep006_5_recommendation_evolution_smoke.py",
    "tests/oep007_autonomous_planner_foundation_smoke.py",
    "tests/oep007_1_planner_safety_gate_smoke.py",
    "tests/oep007_2_plan_risk_scoring_smoke.py",
    "tests/oep007_3_plan_dependency_graph_smoke.py",
    "tests/oep007_4_planner_proposal_bridge_smoke.py",
]

print("ORKIO RELEASE 0.7.0 REGRESSION SUITE")
print("=" * 44)

passed = 0
failed = 0

for test in TESTS:
    if not Path(test).exists():
        print(f"FAIL ...... {test}")
        print(f"Missing test file: {test}\n")
        failed += 1
        continue

    proc = subprocess.run(
        [sys.executable, test],
        text=True,
        capture_output=True,
        env={**dict(), **__import__("os").environ, "PYTHONPATH": "."},
    )
    if proc.returncode == 0:
        print(f"PASS ...... {test}")
        passed += 1
    else:
        print(f"FAIL ...... {test}")
        print(proc.stdout)
        print(proc.stderr)
        failed += 1

print("-" * 44)
print(f"TOTAL PASS: {passed}")
print(f"TOTAL FAIL: {failed}")

if failed:
    raise SystemExit(1)

print("ORKIO_RELEASE_0_7_0_REGRESSION_PASS")
