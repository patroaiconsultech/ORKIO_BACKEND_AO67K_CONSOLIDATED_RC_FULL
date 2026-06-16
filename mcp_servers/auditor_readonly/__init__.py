"""ORKIO MCP Auditor Readonly.

This package exposes a readonly MCP server for defensive audit workflows.
It must not be used as a production write path, deployment path, migration
runner, or secret inspection surface.
"""

__all__ = [
    "audit_trail",
    "auth",
    "config",
    "limits",
    "queries",
    "rbac",
    "sanitizers",
    "schemas",
    "server",
    "tools",
]

__version__ = "0.1.0"
