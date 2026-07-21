"""Offline integrity and contract validation for ORKIO premium package R1.4."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTRACT = "ORKIO-REL-ID-R1.1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_checksums() -> dict[str, Any]:
    checksum_file = ROOT / "SHA256SUMS.txt"
    mismatches: list[dict[str, str]] = []
    checked = 0

    for raw_line in checksum_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        expected, relative_path = line.split("  ", 1)
        target = ROOT / relative_path
        checked += 1
        if not target.is_file():
            mismatches.append(
                {
                    "path": relative_path,
                    "expected": expected,
                    "actual": "missing",
                }
            )
            continue
        actual = _sha256(target)
        if actual != expected:
            mismatches.append(
                {
                    "path": relative_path,
                    "expected": expected,
                    "actual": actual,
                }
            )

    return {
        "checked": checked,
        "mismatches": mismatches,
        "passed": not mismatches,
    }


def _verify_contracts() -> dict[str, Any]:
    main_path = ROOT / "main.py"
    release_path = ROOT / "runtime" / "release_identity.py"
    docker_path = ROOT / "Dockerfile"
    migration_plan_path = ROOT / "scripts" / "preflight_migration_plan.py"
    normalization_path = ROOT / "scripts" / "preflight_alembic_version.py"

    ast.parse(main_path.read_text(encoding="utf-8-sig"))
    release_tree = ast.parse(release_path.read_text(encoding="utf-8-sig"))
    ast.parse(migration_plan_path.read_text(encoding="utf-8-sig"))
    ast.parse(normalization_path.read_text(encoding="utf-8-sig"))

    contract_value = None
    for node in release_tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        if node.targets[0].id != "CONTRACT_VERSION":
            continue
        contract_value = ast.literal_eval(node.value)
        break

    docker_source = docker_path.read_text(encoding="utf-8")
    main_source = main_path.read_text(encoding="utf-8-sig")
    migration_source = migration_plan_path.read_text(encoding="utf-8")
    normalization_source = normalization_path.read_text(encoding="utf-8")

    plan_command = "python scripts/preflight_migration_plan.py"
    normalization_command = "python scripts/preflight_alembic_version.py"
    upgrade_command = "alembic upgrade head"

    checks = {
        "release_identity_contract": contract_value == EXPECTED_CONTRACT,
        "main_contract_enforcement": (
            "CONTRACT_VERSION as _RELID_MODULE_CONTRACT_VERSION"
            in main_source
            and "release_identity_contract_incompatible" in main_source
        ),
        "dual_pythonpath": "ENV PYTHONPATH=/:/app" in docker_source,
        "startup_fail_closed": (
            'logger.exception("ORKIO_BOOT_IDENTITY_FAILED")' in main_source
            and 'app.state.runtime_identity_status = "failed"' in main_source
        ),
        "admin_runtime_identity_gate": (
            '"runtime_identity_validated": bool(' in main_source
            and '"runtime_identity_status": str(' in main_source
            and '"boot_release_identity_source": str(' in main_source
        ),
        "readonly_plan_is_first_database_gate": (
            plan_command in docker_source
            and normalization_command in docker_source
            and upgrade_command in docker_source
            and docker_source.index(plan_command)
            < docker_source.index(normalization_command)
            < docker_source.index(upgrade_command)
        ),
        "migration_plan_has_no_ddl": (
            "CREATE TABLE" not in migration_source.upper()
            and "ALTER TABLE" not in migration_source.upper()
            and '"database_access_mode": "readonly"' in migration_source
        ),
        "production_requires_explicit_migration_policy": (
            "automatic_migration_policy_not_explicit" in migration_source
            and "production_policy_missing" in migration_source
            and "_automatic_migration_policy_explicit" in migration_source
        ),
        "alembic_normalization_requires_explicit_permission": (
            "ALLOW_ALEMBIC_VERSION_NORMALIZATION" in normalization_source
            and "normalization_required_but_not_allowed" in normalization_source
            and 'return False, "default_false"' in normalization_source
        ),
        "module_fallback_parity_test": (
            ROOT / "tests" / "test_release_identity_module_fallback_parity.py"
        ).is_file(),
        "readonly_and_normalization_governance_tests": (
            ROOT / "tests" / "test_migration_plan_governance.py"
        ).is_file()
        and (
            ROOT
            / "tests"
            / "test_alembic_version_normalization_governance.py"
        ).is_file(),
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
    }


def main() -> int:
    result = {
        "package": "ORKIO-PREMIUM-BOOT-RELID-MIGRATION-R1.4",
        "integrity": _verify_checksums(),
        "contracts": _verify_contracts(),
    }
    result["passed"] = (
        result["integrity"]["passed"] and result["contracts"]["passed"]
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
