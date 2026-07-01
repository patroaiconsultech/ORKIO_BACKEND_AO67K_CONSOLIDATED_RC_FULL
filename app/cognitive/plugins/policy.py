from __future__ import annotations

from typing import Any, Dict

from ..contracts import CognitivePlugin, CognitiveRequest, PluginMetadata, PluginResult


class CorePolicyPlugin(CognitivePlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="core.policy",
            version="0.1.0",
            capabilities=["policy"],
            priority=20,
        )

    def evaluate(self, request: CognitiveRequest, state: Dict[str, Any]) -> PluginResult:
        is_superadmin = bool(request.metadata.get("is_superadmin", False))
        mode = state.get("mode", "shadow")

        proposal_only = True
        status = "approved_shadow"

        if is_superadmin and mode == "shadow":
            status = "approved_shadow_superadmin"

        return PluginResult(
            plugin_name=self.metadata().name,
            capability="policy",
            status="ok",
            data={
                "status": status,
                "proposal_only": proposal_only,
                "mode": mode,
                "is_superadmin": is_superadmin,
            },
        )
