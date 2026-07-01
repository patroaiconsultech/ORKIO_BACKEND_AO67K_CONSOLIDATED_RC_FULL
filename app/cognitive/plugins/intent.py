from __future__ import annotations

from typing import Any, Dict

from ..contracts import CognitivePlugin, CognitiveRequest, PluginMetadata, PluginResult


class CoreIntentPlugin(CognitivePlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="core.intent",
            version="0.1.0",
            capabilities=["intent"],
            priority=10,
        )

    def evaluate(self, request: CognitiveRequest, state: Dict[str, Any]) -> PluginResult:
        text = request.message.lower()

        if any(word in text for word in ["patch", "bug", "erro", "deploy", "código", "codigo"]):
            data = {
                "intent": "technical_audit_or_patch",
                "confidence": 0.86,
                "category": "engineering",
                "complexity": "high",
            }
        elif any(word in text for word in ["plano", "business", "investidor", "captação", "captacao"]):
            data = {
                "intent": "business_strategy",
                "confidence": 0.82,
                "category": "strategy",
                "complexity": "medium",
            }
        elif any(word in text for word in ["lembrar", "memória", "memoria", "conversa", "gpt"]):
            data = {
                "intent": "knowledge_ingestion",
                "confidence": 0.9,
                "category": "knowledge",
                "complexity": "medium",
            }
        else:
            data = {
                "intent": "general_chat",
                "confidence": 0.62,
                "category": "general",
                "complexity": "low",
            }

        return PluginResult(
            plugin_name=self.metadata().name,
            capability="intent",
            status="ok",
            data=data,
        )
