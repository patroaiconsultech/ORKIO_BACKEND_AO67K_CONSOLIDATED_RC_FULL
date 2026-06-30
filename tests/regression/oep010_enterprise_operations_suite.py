"""
ORKIO Release 0.10.0 Enterprise Operations mini-suite.

This file is intentionally additive. It does not replace the existing
tests/regression/run_regression_suite.py baseline runner.
"""

from pathlib import Path
import runpy


TEST_FILES = [
    "tests/oep010_1_health_checks_smoke.py",
    "tests/oep010_2_metrics_smoke.py",
    "tests/oep010_3_observability_events_smoke.py",
    "tests/oep010_4_security_audit_smoke.py",
    "tests/oep010_5_operational_readiness_smoke.py",
]


def main() -> int:
    total = 0
    root = Path(__file__).resolve().parents[2]
    for relative_path in TEST_FILES:
        namespace = runpy.run_path(str(root / relative_path))
        test_names = sorted(name for name in namespace if name.startswith("test_"))
        for name in test_names:
            namespace[name]()
            total += 1
        print(f"PASS ...... {relative_path}")
    print("--------------------------------------------")
    print(f"TOTAL PASS: {total}")
    print("TOTAL FAIL: 0")
    print("ORKIO_RELEASE_0_10_0_ENTERPRISE_OPERATIONS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
