from __future__ import annotations

import subprocess
import sys
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
]

def main() -> int:
    passed = 0
    failed = 0
    print("ORKIO RELEASE 0.5.0 REGRESSION SUITE")
    print("=" * 44)

    for test in TESTS:
        path = ROOT / test
        if not path.exists():
            failed += 1
            print(f"MISSING ... {test}")
            continue

        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(ROOT),
            env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
            text=True,
            capture_output=True,
        )

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

    if failed:
        return 1

    print("ORKIO_RELEASE_0_5_0_REGRESSION_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
