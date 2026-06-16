"""Configuration for the Orkio MCP Auditor readonly server."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off", ""}
DEFAULT_TOOLS = (
    "get_health",
    "get_recent_logs_sanitized",
    "get_thread_metadata",
    "get_message_counts",
    "get_file_refs",
    "get_runtime_flags",
    "get_audit_reports",
)
SENSITIVE_NAME_PARTS = (
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "PASS",
    "COOKIE",
    "SESSION",
    "PRIVATE",
    "KEY",
    "CREDENTIAL",
    "DATABASE_URL",
    "DB_URL",
    "DSN",
)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _bool_env(name: str, default: bool = False) -> bool:
    raw = _env(name, "true" if default else "false").lower()
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return default


def _int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = _env(name, str(default))
    try:
        value = int(raw)
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def _csv_env(name: str, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    raw = _env(name, ",".join(default))
    values = tuple(part.strip() for part in raw.split(",") if part.strip())
    return values


def _semicolon_env(name: str) -> tuple[Path, ...]:
    raw = _env(name)
    if not raw:
        return ()
    return tuple(Path(part.strip()) for part in raw.split(";") if part.strip())


def _safe_path_env(name: str, default: str) -> Path:
    return Path(_env(name, default))


@dataclass(frozen=True)
class TableNames:
    threads: str = "threads"
    messages: str = "messages"
    files: str = "files"
    audit_reports: str = "audit_reports"


@dataclass(frozen=True)
class AuditorConfig:
    enabled: bool
    external_auth_required: bool
    principal_id: str
    role: str
    allowed_tools: tuple[str, ...]
    allowed_org_ids: tuple[str, ...]
    database_url: str
    audit_log_path: Path
    log_paths: tuple[Path, ...]
    reports_dir: Path
    runtime_flag_prefixes: tuple[str, ...]
    public_flag_allowlist: tuple[str, ...]
    max_log_lines: int
    max_file_refs: int
    max_audit_reports: int
    max_runtime_flags: int
    table_names: TableNames = field(default_factory=TableNames)

    @property
    def org_scope_is_global(self) -> bool:
        return "*" in self.allowed_org_ids

    @property
    def safe_runtime_prefixes(self) -> tuple[str, ...]:
        prefixes: list[str] = []
        for prefix in self.runtime_flag_prefixes:
            normalized = prefix.strip().upper()
            if normalized and not any(part in normalized for part in SENSITIVE_NAME_PARTS):
                prefixes.append(prefix)
        return tuple(prefixes)

    @classmethod
    def from_env(cls) -> "AuditorConfig":
        table_names = TableNames(
            threads=_env("ORKIO_MCP_AUDITOR_TABLE_THREADS", "threads"),
            messages=_env("ORKIO_MCP_AUDITOR_TABLE_MESSAGES", "messages"),
            files=_env("ORKIO_MCP_AUDITOR_TABLE_FILES", "files"),
            audit_reports=_env("ORKIO_MCP_AUDITOR_TABLE_AUDIT_REPORTS", "audit_reports"),
        )
        return cls(
            enabled=_bool_env("ORKIO_MCP_AUDITOR_ENABLED", False),
            external_auth_required=_bool_env("ORKIO_MCP_AUDITOR_EXTERNAL_AUTH_REQUIRED", True),
            principal_id=_env("ORKIO_MCP_AUDITOR_PRINCIPAL_ID", "mcp_auditor_readonly"),
            role=_env("ORKIO_MCP_AUDITOR_ROLE", "readonly_auditor"),
            allowed_tools=_csv_env("ORKIO_MCP_AUDITOR_ALLOWED_TOOLS", DEFAULT_TOOLS),
            allowed_org_ids=_csv_env("ORKIO_MCP_AUDITOR_ALLOWED_ORG_IDS", ()),
            database_url=_env("ORKIO_MCP_AUDITOR_DATABASE_URL", _env("DATABASE_URL", "")),
            audit_log_path=_safe_path_env("ORKIO_MCP_AUDITOR_AUDIT_LOG_PATH", "./audit/mcp_auditor_readonly.jsonl"),
            log_paths=_semicolon_env("ORKIO_MCP_AUDITOR_LOG_PATHS"),
            reports_dir=_safe_path_env("ORKIO_MCP_AUDITOR_REPORTS_DIR", "./outputs"),
            runtime_flag_prefixes=_csv_env("ORKIO_MCP_AUDITOR_RUNTIME_FLAG_PREFIXES", ("ORKIO_", "FEATURE_", "AO_")),
            public_flag_allowlist=_csv_env("ORKIO_MCP_AUDITOR_PUBLIC_FLAG_ALLOWLIST", ()),
            max_log_lines=_int_env("ORKIO_MCP_AUDITOR_MAX_LOG_LINES", 100, 1, 500),
            max_file_refs=_int_env("ORKIO_MCP_AUDITOR_MAX_FILE_REFS", 50, 1, 200),
            max_audit_reports=_int_env("ORKIO_MCP_AUDITOR_MAX_AUDIT_REPORTS", 50, 1, 200),
            max_runtime_flags=_int_env("ORKIO_MCP_AUDITOR_MAX_RUNTIME_FLAGS", 100, 1, 500),
            table_names=table_names,
        )


@lru_cache(maxsize=1)
def get_config() -> AuditorConfig:
    return AuditorConfig.from_env()


def reload_config() -> AuditorConfig:
    get_config.cache_clear()
    return get_config()
