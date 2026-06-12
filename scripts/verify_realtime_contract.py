from __future__ import annotations

"""Static verifier for the current ORKIO Realtime backend contract.

AO71G replaces the historical verifier that expected ``app/main.py`` and the
obsolete singular ``POST /api/realtime/event`` route. The current repository
keeps ``main.py`` and ``models.py`` at the project root, while the recovery
Realtime router lives in ``routes/realtime.py`` and is injected into the FastAPI
application from ``main.py``.

The verifier is intentionally read-only and uses only the Python standard
library. It does not import the application, connect to a database, call OpenAI,
send e-mail, mutate migrations, or write cache files.
"""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
MODELS = ROOT / "models.py"
REALTIME_ROUTES = ROOT / "routes" / "realtime.py"
REALTIME_SUPPORT = ROOT / "runtime" / "realtime_support.py"
VERSIONS = ROOT / "alembic" / "versions"

REQUIRED_ROUTER_ROUTES = {
    ("POST", "/api/realtime/guard"),
    ("POST", "/api/realtime/client_secret"),
    ("POST", "/api/realtime/start"),
    ("POST", "/api/realtime/events:batch"),
    ("GET", "/api/realtime/{session_id}"),
    ("POST", "/api/realtime/end"),
}

REQUIRED_MAIN_ROUTES = {
    ("GET", "/api/realtime/sessions/{session_id}"),
    ("GET", "/api/realtime/sessions/{session_id}/score"),
    ("POST", "/api/realtime/sessions/{session_id}/review"),
    ("GET", "/api/realtime/sessions/{session_id}/ata.txt"),
}

LEGACY_ROUTES_THAT_MUST_NOT_BE_REQUIRED = {
    ("POST", "/api/realtime/event"),
}

REQUIRED_REALTIME_MIGRATIONS = {
    "0016_patch0100_25S_realtime_audit.py",
    "0017_patch0100_27_1B_realtime_transcript_punct.py",
    "0019_patch0100_28_3_idempotency.py",
    "0026_patch_v64_realtime_schema_reconcile.py",
}


class VerificationFailure(RuntimeError):
    """Raised when a required contract invariant is not satisfied."""


@dataclass(frozen=True)
class MigrationInfo:
    file: Path
    revision: str
    down_revisions: tuple[str, ...]


def fail(message: str) -> None:
    raise VerificationFailure(message)


def ok(message: str) -> None:
    print(f"OK: {message}")


def info(message: str) -> None:
    print(f"INFO: {message}")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def require_paths(paths: Iterable[Path]) -> None:
    missing: list[str] = []
    for path in paths:
        exists = path.is_dir() if path == VERSIONS else path.is_file()
        if not exists:
            missing.append(str(path.relative_to(ROOT)))
    if missing:
        fail(f"project structure incomplete; missing: {', '.join(missing)}")
    ok("current project layout detected")


def parse_python(path: Path) -> tuple[str, ast.Module]:
    source = read_text(path)
    try:
        tree = ast.parse(source, filename=str(path))
        compile(tree, str(path), "exec")
    except SyntaxError as exc:
        fail(
            f"syntax error in {path.relative_to(ROOT)}:"
            f"{exc.lineno}:{exc.offset}: {exc.msg}"
        )
    ok(f"syntax: {path.relative_to(ROOT)}")
    return source, tree


def _decorator_route(decorator: ast.AST) -> tuple[str, str] | None:
    if not isinstance(decorator, ast.Call):
        return None
    func = decorator.func
    if not isinstance(func, ast.Attribute):
        return None

    method = func.attr.upper()
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}:
        return None
    if not decorator.args:
        return None

    path_arg = decorator.args[0]
    if not isinstance(path_arg, ast.Constant) or not isinstance(path_arg.value, str):
        return None

    return method, path_arg.value


def collect_routes(tree: ast.Module) -> set[tuple[str, str]]:
    routes: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            route = _decorator_route(decorator)
            if route:
                routes.add(route)
    return routes


def require_routes(
    actual: set[tuple[str, str]],
    expected: set[tuple[str, str]],
    label: str,
) -> None:
    missing = sorted(expected - actual)
    if missing:
        formatted = ", ".join(f"{method} {path}" for method, path in missing)
        fail(f"{label} missing routes: {formatted}")
    ok(f"{label}: {len(expected)} required routes present")


def verify_router_wiring(main_source: str) -> None:
    required_tokens = (
        "from .routes.realtime import build_realtime_router as _build_realtime_router",
        "app.include_router(_build_realtime_router(",
        "RealtimeEvent=RealtimeEvent",
        "RealtimeSession=RealtimeSession",
        "get_current_user=get_current_user",
        "get_db=get_db",
    )
    missing = [token for token in required_tokens if token not in main_source]
    if missing:
        fail(f"Realtime router wiring incomplete; missing token: {missing[0]}")
    ok("Realtime router is wired into FastAPI with required dependencies")


def class_fields(tree: ast.Module, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            fields: set[str] = set()
            for item in node.body:
                target: ast.AST | None = None
                if isinstance(item, ast.Assign) and item.targets:
                    target = item.targets[0]
                elif isinstance(item, ast.AnnAssign):
                    target = item.target
                if isinstance(target, ast.Name):
                    fields.add(target.id)
            return fields
    fail(f"class missing: {class_name}")
    return set()


def require_class_fields(
    tree: ast.Module,
    class_name: str,
    expected: set[str],
    source_label: str,
) -> None:
    actual = class_fields(tree, class_name)
    missing = sorted(expected - actual)
    if missing:
        fail(
            f"{source_label}.{class_name} missing fields: {', '.join(missing)}"
        )
    ok(f"{source_label}.{class_name}: required fields present")


def verify_models(models_tree: ast.Module) -> None:
    require_class_fields(
        models_tree,
        "RealtimeSession",
        {
            "__tablename__",
            "id",
            "org_slug",
            "thread_id",
            "agent_id",
            "agent_name",
            "user_id",
            "user_name",
            "model",
            "voice",
            "started_at",
            "ended_at",
            "meta",
        },
        "models",
    )
    require_class_fields(
        models_tree,
        "RealtimeEvent",
        {
            "__tablename__",
            "__table_args__",
            "id",
            "org_slug",
            "session_id",
            "thread_id",
            "speaker_type",
            "speaker_id",
            "agent_id",
            "agent_name",
            "event_type",
            "transcript_raw",
            "transcript_punct",
            "created_at",
            "client_event_id",
            "meta",
        },
        "models",
    )


def verify_request_contracts(support_tree: ast.Module) -> None:
    require_class_fields(
        support_tree,
        "RealtimeClientSecretReq",
        {
            "agent_id",
            "voice",
            "model",
            "ttl_seconds",
            "mode",
            "response_profile",
            "language_profile",
        },
        "runtime.realtime_support",
    )
    require_class_fields(
        support_tree,
        "RealtimeStartReq",
        {
            "agent_id",
            "thread_id",
            "voice",
            "model",
            "ttl_seconds",
            "mode",
            "response_profile",
            "language_profile",
        },
        "runtime.realtime_support",
    )
    require_class_fields(
        support_tree,
        "RealtimeEventIn",
        {
            "session_id",
            "event_type",
            "client_event_id",
            "role",
            "content",
            "created_at",
            "is_final",
            "meta",
        },
        "runtime.realtime_support",
    )
    require_class_fields(
        support_tree,
        "RealtimeEndReq",
        {"session_id", "ended_at", "meta"},
        "runtime.realtime_support",
    )
    require_class_fields(
        support_tree,
        "RealtimeGuardReq",
        {"thread_id", "message"},
        "runtime.realtime_support",
    )


def verify_advisory_policy(realtime_source: str) -> None:
    required_tokens = (
        "REALTIME_ADVISORY_RECOMMENDED_SECONDS",
        '"limited": False',
        '"max_seconds": None',
        '"remaining_seconds": None',
        '"cooldown_seconds": 0',
        '"advisory_only": True',
        '"recommended_seconds": REALTIME_ADVISORY_RECOMMENDED_SECONDS',
        '"timebox_policy": "advisory_only_esg"',
    )
    missing = [token for token in required_tokens if token not in realtime_source]
    if missing:
        fail(f"Realtime advisory policy incomplete; missing token: {missing[0]}")

    info(
        "Realtime policy verified as advisory_only_esg; "
        "this verifier does not claim a hard two-minute stop"
    )
    ok("Realtime advisory metadata contract")


def literal_assignment(tree: ast.Module, name: str) -> Any:
    for node in tree.body:
        target_name: str | None = None
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign) and node.targets:
            if isinstance(node.targets[0], ast.Name):
                target_name = node.targets[0].id
                value_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target_name = node.target.id
            value_node = node.value

        if target_name == name and value_node is not None:
            try:
                return ast.literal_eval(value_node)
            except (ValueError, TypeError):
                fail(f"non-literal migration assignment: {name}")
    fail(f"migration assignment missing: {name}")
    return None


def normalize_down_revisions(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (tuple, list)):
        values = tuple(str(item) for item in value if item is not None)
        return values
    fail(f"unsupported down_revision value: {value!r}")
    return ()


def load_migrations() -> list[MigrationInfo]:
    files = sorted(VERSIONS.glob("*.py"))
    if not files:
        fail("no Alembic migrations found")

    migrations: list[MigrationInfo] = []
    for path in files:
        _, tree = parse_python(path)
        revision = literal_assignment(tree, "revision")
        down_revision = literal_assignment(tree, "down_revision")
        if not isinstance(revision, str) or not revision.strip():
            fail(f"invalid revision in {path.name}")
        migrations.append(
            MigrationInfo(
                file=path,
                revision=revision,
                down_revisions=normalize_down_revisions(down_revision),
            )
        )
    return migrations


def verify_migration_chain(migrations: list[MigrationInfo]) -> None:
    by_revision: dict[str, MigrationInfo] = {}
    for migration in migrations:
        if migration.revision in by_revision:
            fail(
                "duplicate Alembic revision "
                f"{migration.revision}: {by_revision[migration.revision].file.name}, "
                f"{migration.file.name}"
            )
        by_revision[migration.revision] = migration

    missing_parents: list[str] = []
    referenced: set[str] = set()
    for migration in migrations:
        for parent in migration.down_revisions:
            referenced.add(parent)
            if parent not in by_revision:
                missing_parents.append(
                    f"{migration.file.name} -> {parent}"
                )

    if missing_parents:
        fail(f"Alembic chain has missing parents: {', '.join(missing_parents)}")

    heads = sorted(set(by_revision) - referenced)
    if len(heads) != 1:
        fail(f"Alembic chain must have exactly one head; found: {heads}")

    expected_files = {path.name for path in VERSIONS.glob("*.py")}
    missing_realtime = sorted(REQUIRED_REALTIME_MIGRATIONS - expected_files)
    if missing_realtime:
        fail(f"missing Realtime migrations: {', '.join(missing_realtime)}")

    ok(
        f"Alembic chain: {len(migrations)} migrations, "
        f"single head {heads[0]}"
    )
    ok("required Realtime migrations present")


def verify_no_duplicate_realtime_routes(
    main_routes: set[tuple[str, str]],
    router_routes: set[tuple[str, str]],
) -> None:
    duplicates = sorted(main_routes & router_routes)
    if duplicates:
        formatted = ", ".join(f"{method} {path}" for method, path in duplicates)
        fail(f"duplicate Realtime route registrations detected: {formatted}")
    ok("no duplicate method/path pairs between main.py and routes/realtime.py")


def main() -> int:
    try:
        require_paths(
            (MAIN, MODELS, REALTIME_ROUTES, REALTIME_SUPPORT, VERSIONS)
        )

        main_source, main_tree = parse_python(MAIN)
        _, models_tree = parse_python(MODELS)
        realtime_source, realtime_tree = parse_python(REALTIME_ROUTES)
        _, support_tree = parse_python(REALTIME_SUPPORT)

        verify_router_wiring(main_source)

        main_routes = {
            route for route in collect_routes(main_tree) if "/api/realtime" in route[1]
        }
        router_routes = {
            route for route in collect_routes(realtime_tree) if "/api/realtime" in route[1]
        }

        require_routes(router_routes, REQUIRED_ROUTER_ROUTES, "Realtime recovery router")
        require_routes(main_routes, REQUIRED_MAIN_ROUTES, "Realtime audit/session routes")
        verify_no_duplicate_realtime_routes(main_routes, router_routes)

        present_legacy = sorted(LEGACY_ROUTES_THAT_MUST_NOT_BE_REQUIRED & (main_routes | router_routes))
        if present_legacy:
            formatted = ", ".join(f"{method} {path}" for method, path in present_legacy)
            info(f"legacy route still present but no longer required: {formatted}")
        else:
            ok("obsolete singular POST /api/realtime/event is not required or registered")

        verify_request_contracts(support_tree)
        verify_models(models_tree)
        verify_advisory_policy(realtime_source)

        migrations = load_migrations()
        verify_migration_chain(migrations)

        print(
            "PASS: current Realtime contract, router wiring, models, "
            "advisory policy and Alembic chain verified"
        )
        return 0
    except VerificationFailure as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
