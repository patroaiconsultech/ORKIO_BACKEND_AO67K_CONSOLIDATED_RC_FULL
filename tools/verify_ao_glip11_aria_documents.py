from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
BRIDGE = ROOT / "runtime" / "glip_aria_document_bridge.py"
TEST = ROOT / "tests" / "test_ao_glip11_aria_documents.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"AO_GLIP11_VERIFY_FAILED: {message}")


def main() -> None:
    for path in (MAIN, BRIDGE, TEST):
        require(path.is_file(), f"missing:{path.relative_to(ROOT)}")
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    main_source = MAIN.read_text(encoding="utf-8")
    bridge_source = BRIDGE.read_text(encoding="utf-8")

    require(
        "execute_glip_aria_document_stream(" in main_source,
        "missing_document_dispatch",
    )
    require(
        "load_glip_aria_document_context(" in main_source,
        "missing_document_context",
    )
    require(
        "GlipAriaDocumentArtifactGenerateIn.model_validate(input_payload)"
        in main_source,
        "missing_trusted_glip_schema",
    )
    require(
        "build_glip_aria_terminal_events(" in main_source,
        "missing_terminal_artifact_envelope",
    )
    require(
        'GLIP_ARIA_DOCUMENT_BRIDGE_VERSION = "AO-GLIP11A"' in bridge_source,
        "wrong_bridge_version",
    )
    require(
        '"agent_name": "Aria"' in bridge_source,
        "aria_identity_not_locked",
    )
    require(
        '"artifact": artifact' in bridge_source
        and '"artifacts": artifacts' in bridge_source,
        "artifact_not_propagated",
    )
    print("AO_GLIP11_VERIFY_OK")


if __name__ == "__main__":
    main()
