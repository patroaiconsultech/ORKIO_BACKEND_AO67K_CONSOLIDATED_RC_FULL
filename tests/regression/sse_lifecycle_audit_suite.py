import subprocess
import sys

TESTS = [
    "tests/sse_lifecycle_audit_smoke.py",
]

def run(cmd):
    return subprocess.run(cmd, text=True)

def main() -> int:
    total_pass = 0
    total_fail = 0

    for test in TESTS:
        result = run([sys.executable, "-m", "pytest", test])
        if result.returncode == 0:
            print(f"PASS ...... {test}")
            total_pass += 1
        else:
            print(f"FAIL ...... {test}")
            total_fail += 1

    print("--------------------------------------------")
    print(f"TOTAL PASS: {total_pass}")
    print(f"TOTAL FAIL: {total_fail}")

    if total_fail:
        return 1

    print("SSE_LIFECYCLE_AUDIT_PATCH_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
