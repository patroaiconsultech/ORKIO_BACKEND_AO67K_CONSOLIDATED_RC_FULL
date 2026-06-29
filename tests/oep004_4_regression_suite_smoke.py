import subprocess
import sys

result = subprocess.run(
    [sys.executable, "tests/regression/run_regression_suite.py"],
    text=True,
    capture_output=True,
)

assert result.returncode == 0, result.stdout + result.stderr
assert "ORKIO_RELEASE_0_5_0_REGRESSION_PASS" in result.stdout

print("OEP004_4_REGRESSION_SUITE_PASS")
