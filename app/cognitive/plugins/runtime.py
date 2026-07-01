from __future__ import annotations

from typing import Any, Dict

from ..contracts import CognitivePlugin, CognitiveRequest, PluginMetadata, PluginResult


class CoreRuntimePlugin(CognitivePlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="core.runtime",
            version="0.1.0",
            capabilities=["runtime"],
            priority=40,
        )

    def evaluate(self, request: CognitiveRequest, state: Dict[str, Any]) -> PluginResult:
        intent = state.get("core.intent", {}).get("intent", "general_chat")
        complexity = state.get("core.intent", {}).get("complexity", "low")

        if intent == "technical_audit_or_patch":
            runtime = "agent.dev"
            executor = "DevAgent"
        elif intent == "business_strategy":
            runtime = "agent.strategy"
            executor = "StrategyAgent"
        elif intent == "knowledge_ingestion":
            runtime = "knowledge.ingestion"
            executor = "KnowledgeIngestion"
        elif complexity == "high":
            runtime = "gpt-5"
            executor = "GeneralReasoningAgent"
        else:
            runtime = "gpt-5-mini"
            executor = "GeneralAgent"

        return PluginResult(
            plugin_name=self.metadata().name,
            capability="runtime",
            status="ok",
            data={"runtime": runtime, "executor": executor},
        )
