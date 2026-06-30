import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(script: str) -> None:
    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="")
        raise SystemExit(result.returncode)

if __name__ == "__main__":
    run("tests/oep012_1_landing_executive_positioning_smoke.py")
