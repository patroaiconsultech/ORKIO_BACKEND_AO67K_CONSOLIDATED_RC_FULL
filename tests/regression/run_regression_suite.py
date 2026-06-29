from __future__ import annotations
import os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TESTS=[
"tests/oep003_knowledge_vault_smoke.py","tests/oep003_1_knowledge_service_smoke.py","tests/oep003_2_knowledge_manifest_governance_smoke.py","tests/oep003_3_evolution_engine_compat_smoke.py",
"tests/oep004_distiller_smoke.py","tests/oep004_1_distiller_knowledge_bridge_smoke.py","tests/oep004_2_batch_idempotency_smoke.py","tests/oep004_3_conversation_intake_governance_smoke.py",
"tests/oep005_proposal_engine_smoke.py","tests/oep005_1_proposal_ranking_smoke.py","tests/oep005_2_conflict_detection_smoke.py","tests/oep005_3_approval_workflow_smoke.py",
"tests/oep006_learning_engine_foundation_smoke.py","tests/oep006_1_learning_memory_smoke.py","tests/oep006_2_outcome_tracker_smoke.py","tests/oep006_3_confidence_calibration_smoke.py","tests/oep006_4_experience_repository_smoke.py","tests/oep006_5_recommendation_evolution_smoke.py",
"tests/oep007_autonomous_planner_foundation_smoke.py","tests/oep007_1_planner_safety_gate_smoke.py","tests/oep007_2_plan_risk_scoring_smoke.py","tests/oep007_3_plan_dependency_graph_smoke.py","tests/oep007_4_planner_proposal_bridge_smoke.py",
"tests/oep008_1_change_package_smoke.py","tests/oep008_2_diff_preview_smoke.py","tests/oep008_3_rollback_generator_smoke.py","tests/oep008_4_approval_pipeline_smoke.py","tests/oep008_5_governance_audit_smoke.py"]
print("ORKIO RELEASE 0.8.0 REGRESSION SUITE"); print("="*44)
passed=failed=0
env=dict(os.environ); env["PYTHONPATH"]=str(ROOT)
for test in TESTS:
    path=ROOT/test
    if not path.exists():
        print(f"FAIL ...... {test}\nMissing file: {test}"); failed+=1; continue
    proc=subprocess.run([sys.executable,str(path)],cwd=str(ROOT),env=env,capture_output=True,text=True)
    if proc.returncode==0:
        print(f"PASS ...... {test}"); passed+=1
    else:
        print(f"FAIL ...... {test}\n{proc.stdout}\n{proc.stderr}"); failed+=1
print("-"*44); print(f"TOTAL PASS: {passed}"); print(f"TOTAL FAIL: {failed}")
if failed: raise SystemExit(1)
print("ORKIO_RELEASE_0_8_0_REGRESSION_PASS")
