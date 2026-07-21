"""Offline integrity and contract validation for ORKIO premium package R1.6."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RELEASE_CONTRACT = "ORKIO-REL-ID-R1.1"
EXPECTED_EVOLUTION_VERSION = "ORKIO-EVOLUTION-INTELLIGENCE-R1.1"
EXPECTED_KPI_REGISTRY = "ORKIO-EVOLUTION-KPI-REGISTRY-R2"
EXPECTED_FOUNDATION_MIGRATION = "0039_patch_evolution_intelligence_foundation"
EXPECTED_PREMIUM_MIGRATION = "0040_patch_evolution_intelligence_premium_lineage"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assignment(path: Path, name: str) -> Any:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        if node.targets[0].id == name:
            return ast.literal_eval(node.value)
    return None


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
                {"path": relative_path, "expected": expected, "actual": "missing"}
            )
            continue
        actual = _sha256(target)
        if actual != expected:
            mismatches.append(
                {"path": relative_path, "expected": expected, "actual": actual}
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
    evolution_governance_path = (
        ROOT / "evolution" / "intelligence" / "governance.py"
    )
    evolution_registry_path = (
        ROOT / "evolution" / "intelligence" / "kpi_registry.py"
    )
    evolution_route_path = ROOT / "routes" / "evolution_intelligence.py"
    evolution_service_path = ROOT / "services" / "evolution_intelligence_service.py"
    evolution_foundation_migration_path = (
        ROOT
        / "alembic"
        / "versions"
        / "0039_patch_evolution_intelligence_foundation.py"
    )
    evolution_premium_migration_path = (
        ROOT
        / "alembic"
        / "versions"
        / "0040_patch_evolution_intelligence_premium_lineage.py"
    )

    paths = [
        main_path,
        release_path,
        migration_plan_path,
        normalization_path,
        evolution_governance_path,
        evolution_registry_path,
        evolution_route_path,
        evolution_service_path,
        evolution_foundation_migration_path,
        evolution_premium_migration_path,
    ]
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8-sig"))

    docker_source = docker_path.read_text(encoding="utf-8")
    main_source = main_path.read_text(encoding="utf-8-sig")
    migration_source = migration_plan_path.read_text(encoding="utf-8")
    normalization_source = normalization_path.read_text(encoding="utf-8")
    governance_source = evolution_governance_path.read_text(encoding="utf-8")
    registry_source = evolution_registry_path.read_text(encoding="utf-8")
    route_source = evolution_route_path.read_text(encoding="utf-8")
    service_source = evolution_service_path.read_text(encoding="utf-8")
    evolution_foundation_migration_source = (
        evolution_foundation_migration_path.read_text(encoding="utf-8")
    )
    evolution_premium_migration_source = (
        evolution_premium_migration_path.read_text(encoding="utf-8")
    )

    plan_command = "python scripts/preflight_migration_plan.py"
    normalization_command = "python scripts/preflight_alembic_version.py"
    upgrade_command = "alembic upgrade head"

    checks = {
        "release_identity_contract": (
            _assignment(release_path, "CONTRACT_VERSION")
            == EXPECTED_RELEASE_CONTRACT
        ),
        "main_release_contract_enforcement": (
            "CONTRACT_VERSION as _RELID_MODULE_CONTRACT_VERSION" in main_source
            and "release_identity_contract_incompatible" in main_source
        ),
        "dual_pythonpath": "ENV PYTHONPATH=/:/app" in docker_source,
        "startup_fail_closed": (
            'logger.exception("ORKIO_BOOT_IDENTITY_FAILED")' in main_source
            and 'app.state.runtime_identity_status = "failed"' in main_source
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
        ),
        "alembic_normalization_requires_explicit_permission": (
            "ALLOW_ALEMBIC_VERSION_NORMALIZATION" in normalization_source
            and "normalization_required_but_not_allowed" in normalization_source
        ),
        "evolution_version": (
            _assignment(
                evolution_governance_path,
                "EVOLUTION_INTELLIGENCE_VERSION",
            )
            == EXPECTED_EVOLUTION_VERSION
        ),
        "evolution_fail_closed_governance": (
            "auto_apply_not_allowed_in_foundation_r1" in governance_source
            and "code_write_not_allowed_in_foundation_r1" in governance_source
            and "production_requires_human_approval" in governance_source
            and "production_requires_proposal_only" in governance_source
        ),
        "formal_kpi_registry": (
            _assignment(evolution_registry_path, "KPI_REGISTRY_VERSION")
            == EXPECTED_KPI_REGISTRY
            and "REQUIRED_KPI_FIELDS" in registry_source
            and "collector_version" in registry_source
            and "source_version" in registry_source
            and "auto_apply_enabled: bool = False" in registry_source
            and "PROJECT_HEALTH_WEIGHTS" in registry_source
        ),
        "tenant_scoped_routes": (
            "deps.get_request_org(admin, x_org_slug)" in route_source
            and "/api/admin/evolution/intelligence" in route_source
            and "EVOLUTION_CONFIG_WRITE_DISABLED" in route_source
            and "HUMAN_APPROVAL_REQUIRED" in route_source
        ),
        "tenant_scoped_queries": (
            "WHERE id = :objective_id AND org_slug = :org_slug" in service_source
            and "WHERE org_slug = :org_slug" in service_source
            and "OBJECTIVE_NOT_FOUND" in service_source
        ),
        "proposal_only_preview": (
            '"mode": "proposal_only"' in service_source
            and '"auto_apply": False' in service_source
            and '"write_executed": False' in service_source
        ),
        "migration_chain": (
            _assignment(evolution_foundation_migration_path, "revision")
            == EXPECTED_FOUNDATION_MIGRATION
            and _assignment(
                evolution_foundation_migration_path,
                "down_revision",
            )
            == "0038_patch_auth_password_reset_tokens"
            and _assignment(evolution_premium_migration_path, "revision")
            == EXPECTED_PREMIUM_MIGRATION
            and _assignment(
                evolution_premium_migration_path,
                "down_revision",
            )
            == EXPECTED_FOUNDATION_MIGRATION
        ),
        "database_tenant_constraints": (
            "scope_key" in evolution_foundation_migration_source
            and "fk_evolution_kpi_target_objective_org"
            in evolution_foundation_migration_source
            and "fk_evolution_health_objective_org"
            in evolution_foundation_migration_source
            and "ux_evolution_objective_org_name"
            in evolution_foundation_migration_source
            and "fk_evolution_target_version_objective_org"
            in evolution_premium_migration_source
        ),
        "runtime_governance_identity": (
            "evolution_governance_validated" in route_source
            and "evolution_governance_consistent" in route_source
            and "kpi_registry_version" in route_source
            and "runtime_governance_identity" in route_source
        ),
        "kpi_provenance": (
            "collector_version" in service_source
            and "source_version" in service_source
            and "content_sha256" in service_source
            and "evolution_health_snapshot_provenance"
            in evolution_premium_migration_source
        ),
        "immutable_health_snapshots": (
            "ORKIO_IMMUTABLE_RECORD" in evolution_premium_migration_source
            and "BEFORE UPDATE OR DELETE"
            in evolution_premium_migration_source
            and "evolution_health_snapshot_events"
            in evolution_premium_migration_source
            and "invalidate_health_snapshot" in service_source
        ),
        "versioned_targets": (
            "evolution_kpi_target_versions"
            in evolution_premium_migration_source
            and "effective_from" in evolution_premium_migration_source
            and "effective_to" in evolution_premium_migration_source
            and "change_reason" in evolution_premium_migration_source
            and "approval_id" in evolution_premium_migration_source
            and "/targets/history" in route_source
        ),
        "explicit_health_coverage": (
            "health_coverage" in service_source
            and "unknown_kpis" in service_source
            and "stale_kpis" in service_source
            and "blockers" in service_source
        ),
        "main_evolution_wiring": (
            "build_evolution_intelligence_router" in main_source
            and "_startup_evolution_intelligence_governance_r1" in main_source
            and "EVOLUTION_INTELLIGENCE_GOVERNANCE_FAILED" in main_source
            and "actor_reference=actor_reference" in main_source
        ),
        "evolution_test_suite_present": (
            ROOT / "tests" / "evolution_intelligence" / "test_registry.py"
        ).is_file()
        and (
            ROOT / "tests" / "evolution_intelligence" / "test_routes.py"
        ).is_file()
        and (
            ROOT
            / "tests"
            / "evolution_intelligence"
            / "test_service_tenant_isolation.py"
        ).is_file(),
    }

    return {"checks": checks, "passed": all(checks.values())}


def main() -> int:
    result = {
        "package": "ORKIO-EVOLUTION-INTELLIGENCE-PREMIUM-R1.6",
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
