from __future__ import annotations

from typing import Any, Dict, List

from .contracts import CognitiveRequest, PluginResult
from .envelope import DecisionEnvelope
from .event_bus import InMemoryEventBus
from .registry import PluginRegistry


class CognitiveMicrokernel:
    """Microkernel responsible only for receive, evaluate, plan, dispatch, observe.

    It does not call LLM providers, databases, HTTP routes, or frontend code.
    """

    def __init__(
        self,
        registry: PluginRegistry,
        event_bus: InMemoryEventBus | None = None,
        mode: str = "shadow",
    ) -> None:
        self.registry = registry
        self.event_bus = event_bus or InMemoryEventBus()
        self.mode = mode

    def handle(self, request: CognitiveRequest) -> DecisionEnvelope:
        self.event_bus.publish("RequestReceived", {"request_id": request.request_id})

        state: Dict[str, Any] = {"request": request, "mode": self.mode}
        results: List[PluginResult] = []

        for plugin in self.registry.enabled():
            result = plugin.evaluate(request, state)
            results.append(result)
            state[plugin.metadata().name] = result.data
            self.event_bus.publish(
                "PluginEvaluated",
                {
                    "request_id": request.request_id,
                    "plugin": plugin.metadata().name,
                    "capability": result.capability,
                    "status": result.status,
                },
            )

        envelope = self._build_envelope(request, state, results)
        self.event_bus.publish("DecisionEnvelopeBuilt", envelope.to_dict())
        return envelope

    def _build_envelope(
        self,
        request: CognitiveRequest,
        state: Dict[str, Any],
        results: List[PluginResult],
    ) -> DecisionEnvelope:
        intent = state.get("core.intent", {})
        runtime = state.get("core.runtime", {})
        policy = state.get("core.policy", {})
        risk = state.get("core.risk", {})

        envelope = DecisionEnvelope(
            request_id=request.request_id,
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            mode=self.mode,
            intent=intent.get("intent"),
            confidence=float(intent.get("confidence", 0.0)),
            category=intent.get("category"),
            complexity=intent.get("complexity", "unknown"),
            runtime=runtime.get("runtime"),
            executor=runtime.get("executor"),
            policy_status=policy.get("status", "unknown"),
            risk_level=risk.get("risk_level", "unknown"),
            proposal_only=policy.get("proposal_only", True),
            plan=self._plan(state),
            plugin_results=[
                {
                    "plugin_name": result.plugin_name,
                    "capability": result.capability,
                    "status": result.status,
                    "data": result.data,
                    "error": result.error,
                }
                for result in results
            ],
        )
        return envelope

    def _plan(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        intent = state.get("core.intent", {}).get("intent", "general_chat")
        runtime = state.get("core.runtime", {}).get("runtime", "default_llm")
        risk = state.get("core.risk", {}).get("risk_level", "unknown")

        plan = [
            {"step": 1, "action": "load_context", "status": "planned"},
            {"step": 2, "action": f"route_intent:{intent}", "status": "planned"},
            {"step": 3, "action": f"use_runtime:{runtime}", "status": "planned"},
        ]

        if risk in {"high", "critical"}:
            plan.append({"step": 4, "action": "require_human_approval", "status": "planned"})
        else:
            plan.append({"step": 4, "action": "dispatch_to_orchestrator", "status": "planned"})

        return plan
