from __future__ import annotations

from ..registry import PluginRegistry
from .intent import CoreIntentPlugin
from .policy import CorePolicyPlugin
from .risk import CoreRiskPlugin
from .runtime import CoreRuntimePlugin


def register_core_plugins(registry: PluginRegistry) -> PluginRegistry:
    registry.register(CoreIntentPlugin())
    registry.register(CorePolicyPlugin())
    registry.register(CoreRiskPlugin())
    registry.register(CoreRuntimePlugin())
    return registry
