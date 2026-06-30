"""
ORKIO Release 0.10.1 Enterprise Operations Hardening mini-suite.

Additive runner. It does not replace the v0.10.0 or v0.9.0 regression suites.
"""

from pathlib import Path
import runpy


TEST_FILES = [
    "tests/oep010_6_enterprise_hardening_smoke.py",
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
    print("ORKIO_RELEASE_0_10_1_ENTERPRISE_OPERATIONS_HARDENING_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
