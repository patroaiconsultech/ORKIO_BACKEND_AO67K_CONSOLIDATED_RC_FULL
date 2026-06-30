import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

tests = [
    "tests/cp002_mission_kernel_smoke.py",
]

total_pass = 0
total_fail = 0

for test in tests:
    result = subprocess.run(
        ["pytest", test],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if result.returncode == 0:
        total_pass += 1
        print(f"PASS ...... {test}")
    else:
        total_fail += 1
        print(f"FAIL ...... {test}")
        print(result.stdout)
        print(result.stderr)

print("--------------------------------------------")
print(f"TOTAL PASS: {total_pass}")
print(f"TOTAL FAIL: {total_fail}")

if total_fail:
    raise SystemExit(1)

print("CP002_MISSION_KERNEL_FOUNDATION_PASS")
