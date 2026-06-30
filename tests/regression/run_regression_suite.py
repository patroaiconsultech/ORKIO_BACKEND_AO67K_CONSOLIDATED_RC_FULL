from __future__ import annotations
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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
    "tests/oep008_1_change_package_smoke.py",
    "tests/oep008_2_diff_preview_smoke.py",
    "tests/oep008_3_rollback_generator_smoke.py",
    "tests/oep008_4_approval_pipeline_smoke.py",
    "tests/oep008_5_governance_audit_smoke.py",
    "tests/oep009_1_organization_service_smoke.py",
    "tests/oep009_2_workspace_service_smoke.py",
    "tests/oep009_3_project_service_smoke.py",
    "tests/oep009_4_rbac_smoke.py",
    "tests/oep009_5_audit_log_smoke.py",
]
print("ORKIO RELEASE 0.9.0 REGRESSION SUITE")
print("=" * 44)
passed = failed = skipped = 0
env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT)
for test in TESTS:
    path = ROOT / test
    if not path.exists():
        skipped += 1
        print(f"SKIP ...... {test}")
        continue
    result = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), env=env, capture_output=True, text=True)
    if result.returncode == 0:
        passed += 1
        print(f"PASS ...... {test}")
    else:
        failed += 1
        print(f"FAIL ...... {test}")
        print(result.stdout)
        print(result.stderr)
print("-" * 44)
print(f"TOTAL PASS: {passed}")
print(f"TOTAL FAIL: {failed}")
if skipped:
    print(f"TOTAL SKIP: {skipped}")
if failed:
    sys.exit(1)
print("ORKIO_RELEASE_0_9_0_REGRESSION_PASS")
