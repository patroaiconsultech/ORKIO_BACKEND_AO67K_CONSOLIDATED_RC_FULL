from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time
import uuid


@dataclass(frozen=True)
class CognitiveRequest:
    """Canonical input for the Cognitive Microkernel.

    This object is intentionally independent from FastAPI, database models,
    OpenAI providers, and frontend DTOs.
    """

    user_id: str
    tenant_id: str
    message: str
    thread_id: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    capabilities: List[str]
    priority: int = 100
    enabled: bool = True


@dataclass
class PluginResult:
    plugin_name: str
    capability: str
    status: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class CognitivePlugin(ABC):
    """Base contract for all Cognitive Kernel plugins.

    Plugins may evaluate requests, execute safe deterministic work,
    expose health, and provide rollback instructions.
    """

    @abstractmethod
    def metadata(self) -> PluginMetadata:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, request: CognitiveRequest, state: Dict[str, Any]) -> PluginResult:
        raise NotImplementedError

    def execute(self, plan: Dict[str, Any], state: Dict[str, Any]) -> PluginResult:
        return PluginResult(
            plugin_name=self.metadata().name,
            capability="execute",
            status="skipped",
            data={"reason": "plugin does not implement execution"},
        )

    def rollback(self, execution_id: str, state: Dict[str, Any]) -> PluginResult:
        return PluginResult(
            plugin_name=self.metadata().name,
            capability="rollback",
            status="noop",
            data={"execution_id": execution_id},
        )

    def health(self) -> Dict[str, Any]:
        meta = self.metadata()
        return {
            "name": meta.name,
            "version": meta.version,
            "enabled": meta.enabled,
            "capabilities": meta.capabilities,
            "status": "ok",
        }
