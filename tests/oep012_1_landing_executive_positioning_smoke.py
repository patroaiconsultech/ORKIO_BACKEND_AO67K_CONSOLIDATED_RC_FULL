from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def assert_contains(path: Path, expected: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert expected in text, f"{expected!r} missing from {path}"

def test_landing_positioning_document_exists() -> None:
    path = ROOT / "docs" / "experience" / "ORKIO_OS_LANDING_EXECUTIVE_POSITIONING.md"
    assert path.exists()
    assert_contains(path, "Cognitive Operating System")
    assert_contains(path, "Start a Mission")
    assert_contains(path, "Platform Core")
    assert_contains(path, "Cognitive Core")
    assert_contains(path, "Experience Core")
    assert_contains(path, "Governance Core")
    assert_contains(path, "Mission Runtime")
    assert_contains(path, "Context before response.")
    assert_contains(path, "Evidence before hypothesis.")
    assert_contains(path, "Mission before task.")

def test_landing_copy_contract_exists() -> None:
    path = ROOT / "docs" / "product" / "orkio_os_landing_copy.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["release"] == "0.10.3"
    assert data["positioning"]["category"] == "Cognitive Operating System"
    assert data["hero"]["primary_cta"] == "Start a Mission"
    assert "Governance Core" in data["cores"]

def test_release_doc_declares_runtime_untouched() -> None:
    path = ROOT / "docs" / "releases" / "ORKIO_RELEASE_0_10_3_LANDING_EXECUTIVE_POSITIONING.md"
    assert path.exists()
    assert_contains(path, "This release does not change runtime behavior.")
    assert_contains(path, "FastAPI changes")
    assert_contains(path, "Runtime changes")
    assert_contains(path, "ORKIO_RELEASE_0_10_3_LANDING_EXECUTIVE_POSITIONING_PASS")

if __name__ == "__main__":
    tests = [
        test_landing_positioning_document_exists,
        test_landing_copy_contract_exists,
        test_release_doc_declares_runtime_untouched,
    ]
    total_pass = 0
    total_fail = 0
    for test in tests:
        try:
            test()
            print(f"PASS ...... {test.__name__}")
            total_pass += 1
        except Exception as exc:
            print(f"FAIL ...... {test.__name__}: {exc}")
            total_fail += 1
    print("--------------------------------------------")
    print(f"TOTAL PASS: {total_pass}")
    print(f"TOTAL FAIL: {total_fail}")
    if total_fail:
        raise SystemExit(1)
    print("ORKIO_RELEASE_0_10_3_LANDING_EXECUTIVE_POSITIONING_PASS")
