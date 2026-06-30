from pathlib import Path
import runpy
import traceback

ROOT = Path(__file__).resolve().parents[2]
TEST_FILES = [ROOT / "tests" / "oep011_1_orkio_os_architecture_smoke.py"]

def run_suite() -> int:
    total_pass = 0
    total_fail = 0
    for test_file in TEST_FILES:
        namespace = runpy.run_path(str(test_file))
        test_functions = [(name, fn) for name, fn in namespace.items() if name.startswith("test_") and callable(fn)]
        for name, fn in test_functions:
            try:
                fn()
                total_pass += 1
                print(f"PASS {test_file.name}::{name}")
            except Exception:
                total_fail += 1
                print(f"FAIL {test_file.name}::{name}")
                traceback.print_exc()
    print(f"TOTAL PASS: {total_pass}")
    print(f"TOTAL FAIL: {total_fail}")
    if total_fail == 0:
        print("ORKIO_RELEASE_0_10_2_OS_ARCHITECTURE_FOUNDATION_PASS")
        return 0
    return 1

if __name__ == "__main__":
    raise SystemExit(run_suite())
