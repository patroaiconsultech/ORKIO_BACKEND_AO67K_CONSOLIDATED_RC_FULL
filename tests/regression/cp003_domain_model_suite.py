import subprocess
import sys


TESTS = [
    "tests/cp003_domain_model_smoke.py",
]


def main() -> int:
    total_pass = 0
    total_fail = 0

    for test in TESTS:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test],
            text=True,
        )
        if result.returncode == 0:
            total_pass += 1
            print(f"PASS ...... {test}")
        else:
            total_fail += 1
            print(f"FAIL ...... {test}")

    print("--------------------------------------------")
    print(f"TOTAL PASS: {total_pass}")
    print(f"TOTAL FAIL: {total_fail}")

    if total_fail == 0:
        print("CP003_DOMAIN_MODEL_FOUNDATION_PASS")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
