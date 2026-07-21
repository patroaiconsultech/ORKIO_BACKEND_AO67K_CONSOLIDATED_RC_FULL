from __future__ import annotations

import ast
import hashlib
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from sqlalchemy import text


CONTRACT_VERSION = "ORKIO-REL-ID-R1.1"

_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")
_SAFE_TEXT_RE = re.compile(r"[^A-Za-z0-9._/@:+-]+")

_COMMIT_ENV_KEYS: Sequence[str] = (
    "ORKIO_COMMIT_SHA",
    "RAILWAY_GIT_COMMIT_SHA",
    "GIT_COMMIT_SHA",
    "SOURCE_COMMIT_SHA",
)
_BRANCH_ENV_KEYS: Sequence[str] = (
    "ORKIO_GIT_BRANCH",
    "RAILWAY_GIT_BRANCH",
    "GIT_BRANCH",
    "SOURCE_BRANCH",
)
_DEPLOYMENT_ENV_KEYS: Sequence[str] = (
    "ORKIO_DEPLOYMENT_ID",
    "RAILWAY_DEPLOYMENT_ID",
)
_BUILD_TIME_ENV_KEYS: Sequence[str] = (
    "ORKIO_BUILD_TIMESTAMP",
    "BUILD_TIMESTAMP",
    "SOURCE_DATE_EPOCH",
)

_GOVERNANCE_FLAG_NAMES: Sequence[str] = (
    "EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED",
    "EVOLUTION_MARCO_ZERO_WRITE_ENABLED",
    "EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED",
    "EVOLUTION_AGENT_EVAL_WRITE_ENABLED",
)


def _first_env(environ: Mapping[str, str], names: Iterable[str]) -> str:
    for name in names:
        raw = str(environ.get(name) or "").strip()
        if raw:
            return raw
    return ""


def _safe_text(value: Any, *, default: str = "unknown", max_length: int = 160) -> str:
    raw = str(value or "").strip()
    if not raw:
        return default
    sanitized = _SAFE_TEXT_RE.sub("_", raw)
    sanitized = sanitized.strip("._")
    if not sanitized:
        return default
    return sanitized[:max_length]


def _safe_commit(value: Any) -> str:
    raw = str(value or "").strip()
    if not _COMMIT_RE.fullmatch(raw):
        return "unknown"
    return raw.lower()


def _env_flag(environ: Mapping[str, str], name: str, *, default: bool = False) -> bool:
    raw = environ.get(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return "unavailable"


def actor_reference(value: Any) -> str:
    """Return a stable non-reversible reference suitable for audit logs."""
    raw = str(value or "").strip().lower()
    if not raw:
        return "actor:unknown"
    return "actor_sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def _assignment_value(tree: ast.AST, name: str) -> Any:
    for node in getattr(tree, "body", []):
        target_name: Optional[str] = None
        value_node: Optional[ast.AST] = None
        if isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target_name = node.targets[0].id
                value_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target_name = node.target.id
            value_node = node.value
        if target_name != name or value_node is None:
            continue
        try:
            return ast.literal_eval(value_node)
        except Exception:
            return None
    return None


def detect_migration_heads(repo_root: Path) -> Sequence[str]:
    versions_dir = repo_root / "alembic" / "versions"
    if not versions_dir.is_dir():
        return ()

    revisions = set()
    referenced = set()
    for path in sorted(versions_dir.glob("*.py")):
        if path.name.startswith("__"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue

        revision = _assignment_value(tree, "revision")
        down_revision = _assignment_value(tree, "down_revision")
        if isinstance(revision, str) and revision.strip():
            revisions.add(revision.strip())

        if isinstance(down_revision, str) and down_revision.strip():
            referenced.add(down_revision.strip())
        elif isinstance(down_revision, (tuple, list, set)):
            referenced.update(
                str(item).strip()
                for item in down_revision
                if isinstance(item, str) and str(item).strip()
            )

    return tuple(sorted(revisions - referenced))


def detect_database_revisions(database: Any) -> Tuple[Tuple[str, ...], str]:
    """Read Alembic revisions without mutating database state.

    Accepts either a SQLAlchemy Session/Connection or an Engine. Only the
    exception class name is surfaced, preventing credentials or SQL text from
    leaking into the release identity payload.
    """
    if database is None:
        return (), "not_queried"

    connection = None
    close_connection = False
    try:
        if hasattr(database, "connect") and not hasattr(database, "execute"):
            connection = database.connect()
            close_connection = True
        else:
            connection = database

        result = connection.execute(
            text("SELECT version_num FROM alembic_version ORDER BY version_num")
        )
        values = result.scalars().all()
        revisions = tuple(
            sorted(
                {
                    str(value).strip()
                    for value in values
                    if str(value or "").strip()
                }
            )
        )
        return revisions, "ok"
    except Exception as exc:
        return (), "error:" + exc.__class__.__name__
    finally:
        if close_connection and connection is not None:
            try:
                connection.close()
            except Exception:
                pass


def build_release_identity(
    app: Any,
    *,
    app_version: str,
    repo_root: Optional[Path] = None,
    runtime_main_path: Optional[Path] = None,
    environ: Optional[Mapping[str, str]] = None,
    database: Any = None,
    authenticated_org: Optional[str] = None,
    authority_scope: Optional[str] = None,
) -> Dict[str, Any]:
    env = dict(os.environ if environ is None else environ)
    root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
    main_path = Path(runtime_main_path or (root / "main.py")).resolve()

    commit_sha = _safe_commit(_first_env(env, _COMMIT_ENV_KEYS))
    branch = _safe_text(_first_env(env, _BRANCH_ENV_KEYS), max_length=128)
    deployment_id = _safe_text(_first_env(env, _DEPLOYMENT_ENV_KEYS), max_length=160)
    build_timestamp = _safe_text(
        _first_env(env, _BUILD_TIME_ENV_KEYS),
        default="unknown",
        max_length=80,
    )
    runtime_main_sha256 = sha256_file(main_path)
    code_heads = list(detect_migration_heads(root))
    database_revisions, database_revision_status = detect_database_revisions(database)
    database_revision_list = list(database_revisions)
    if database_revision_status == "ok":
        migration_in_sync: Optional[bool] = sorted(code_heads) == sorted(database_revision_list)
    else:
        migration_in_sync = None

    explicit_release_id = _safe_text(
        env.get("ORKIO_RELEASE_ID"),
        default="",
        max_length=160,
    )
    if explicit_release_id:
        release_id = explicit_release_id
    elif commit_sha != "unknown":
        release_id = f"orkio-{commit_sha[:12]}"
    else:
        release_id = f"orkio-file-{runtime_main_sha256[:12]}"

    governance_flags = {
        name: _env_flag(env, name, default=False)
        for name in _GOVERNANCE_FLAG_NAMES
    }

    routes = getattr(app, "routes", ()) or ()
    return {
        "contract_version": CONTRACT_VERSION,
        "release_id": release_id,
        "app_version": str(app_version or "unknown"),
        "environment": _safe_text(env.get("APP_ENV"), default="unknown", max_length=64),
        "commit_sha": commit_sha,
        "branch": branch,
        "deployment_id": deployment_id,
        "build_timestamp": build_timestamp,
        "migration_code_heads": code_heads,
        "migration_database_revisions": database_revision_list,
        "migration_database_revision": (
            database_revision_list[0]
            if len(database_revision_list) == 1
            else ("unknown" if not database_revision_list else ",".join(database_revision_list))
        ),
        "migration_database_status": database_revision_status,
        "migration_in_sync": migration_in_sync,
        "route_count": len(routes),
        "runtime_main_path": str(main_path),
        "runtime_main_sha256": runtime_main_sha256,
        "authenticated_org": _safe_text(
            authenticated_org,
            default="not_applicable",
            max_length=128,
        ),
        "authority_scope": _safe_text(
            authority_scope,
            default="not_applicable",
            max_length=64,
        ),
        "governance_flags": governance_flags,
    }


def emit_boot_identity(
    logger: logging.Logger,
    app: Any,
    *,
    app_version: str,
    repo_root: Optional[Path] = None,
    runtime_main_path: Optional[Path] = None,
    environ: Optional[Mapping[str, str]] = None,
    database: Any = None,
) -> Dict[str, Any]:
    identity = build_release_identity(
        app,
        app_version=app_version,
        repo_root=repo_root,
        runtime_main_path=runtime_main_path,
        environ=environ,
        database=database,
    )
    logger.info(
        "ORKIO_BOOT_IDENTITY "
        "contract_version=%s release_id=%s commit_sha=%s branch=%s "
        "deployment_id=%s migration_code_heads=%s migration_database_revisions=%s "
        "migration_database_status=%s migration_in_sync=%s route_count=%s "
        "runtime_main_path=%s runtime_main_sha256=%s "
        "marco_zero_preview_enabled=%s marco_zero_write_enabled=%s "
        "signals_snapshot_write_enabled=%s agent_eval_write_enabled=%s",
        identity["contract_version"],
        identity["release_id"],
        identity["commit_sha"],
        identity["branch"],
        identity["deployment_id"],
        ",".join(identity["migration_code_heads"]) or "unknown",
        ",".join(identity["migration_database_revisions"]) or "unknown",
        identity["migration_database_status"],
        identity["migration_in_sync"],
        identity["route_count"],
        identity["runtime_main_path"],
        identity["runtime_main_sha256"],
        identity["governance_flags"]["EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED"],
        identity["governance_flags"]["EVOLUTION_MARCO_ZERO_WRITE_ENABLED"],
        identity["governance_flags"]["EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED"],
        identity["governance_flags"]["EVOLUTION_AGENT_EVAL_WRITE_ENABLED"],
    )
    return identity
