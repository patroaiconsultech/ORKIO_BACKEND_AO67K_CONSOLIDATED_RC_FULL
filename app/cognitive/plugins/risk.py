from __future__ import annotations

from typing import Any, Dict

from ..contracts import CognitivePlugin, CognitiveRequest, PluginMetadata, PluginResult


class CoreRiskPlugin(CognitivePlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="core.risk",
            version="0.1.0",
            capabilities=["risk"],
            priority=30,
        )

    def evaluate(self, request: CognitiveRequest, state: Dict[str, Any]) -> PluginResult:
        text = request.message.lower()
        critical_terms = ["delete", "excluir", "drop table", "produção", "producao", "deploy", "pagamento"]
        high_terms = ["alterar banco", "rodar código", "executar código", "token", "secret"]

        if any(term in text for term in critical_terms):
            level = "critical"
        elif any(term in text for term in high_terms):
            level = "high"
        elif state.get("core.intent", {}).get("complexity") == "high":
            level = "medium"
        else:
            level = "low"

        return PluginResult(
            plugin_name=self.metadata().name,
            capability="risk",
            status="ok",
            data={"risk_level": level},
        )
