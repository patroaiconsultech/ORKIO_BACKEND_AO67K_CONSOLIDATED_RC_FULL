import subprocess
import sys

proc = subprocess.run(
    [sys.executable, "tests/regression/run_regression_suite.py"],
    text=True,
    capture_output=True,
    env={**__import__("os").environ, "PYTHONPATH": "."},
)

if proc.returncode != 0:
    print(proc.stdout)
    print(proc.stderr)
    raise SystemExit(proc.returncode)

assert "ORKIO_RELEASE_0_7_0_REGRESSION_PASS" in proc.stdout
print("OEP007_5_RELEASE_0_7_REGRESSION_PASS")
