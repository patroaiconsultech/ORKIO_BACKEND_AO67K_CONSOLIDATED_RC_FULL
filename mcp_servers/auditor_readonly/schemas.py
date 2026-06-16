"""Pydantic response schemas for the readonly MCP Auditor."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class BaseToolResponse(BaseModel):
    ok: bool
    tool: str
    correlation_id: str


class ErrorResponse(BaseToolResponse):
    ok: Literal[False] = False
    error: dict[str, str]


class HealthResponse(BaseToolResponse):
    ok: Literal[True] = True
    status: str
    database: dict[str, Any]
    external_auth_required: bool
    enabled: bool
    readonly: bool = True


class LogsResponse(BaseToolResponse):
    ok: Literal[True] = True
    source_configured: bool
    lines: list[dict[str, Any]]


class ThreadMetadataResponse(BaseToolResponse):
    ok: Literal[True] = True
    thread: dict[str, Any] | None


class MessageCountsResponse(BaseToolResponse):
    ok: Literal[True] = True
    thread_ref: str | None
    counts: dict[str, Any]


class FileRefsResponse(BaseToolResponse):
    ok: Literal[True] = True
    thread_ref: str | None
    files: list[dict[str, Any]]


class RuntimeFlagsResponse(BaseToolResponse):
    ok: Literal[True] = True
    flags: dict[str, str] = Field(default_factory=dict)


class AuditReportsResponse(BaseToolResponse):
    ok: Literal[True] = True
    reports: list[dict[str, Any]]
