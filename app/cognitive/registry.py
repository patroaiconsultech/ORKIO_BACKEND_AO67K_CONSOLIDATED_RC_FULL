from __future__ import annotations

from typing import Dict, Iterable, List

from .contracts import CognitivePlugin


class PluginRegistry:
    """Registry that keeps the kernel decoupled from plugin implementations."""

    def __init__(self) -> None:
        self._plugins: Dict[str, CognitivePlugin] = {}

    def register(self, plugin: CognitivePlugin) -> None:
        meta = plugin.metadata()
        if meta.name in self._plugins:
            raise ValueError(f"Plugin already registered: {meta.name}")
        self._plugins[meta.name] = plugin

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def all(self) -> List[CognitivePlugin]:
        return sorted(
            self._plugins.values(),
            key=lambda plugin: plugin.metadata().priority,
        )

    def enabled(self) -> List[CognitivePlugin]:
        return [plugin for plugin in self.all() if plugin.metadata().enabled]

    def by_capability(self, capability: str) -> List[CognitivePlugin]:
        return [
            plugin
            for plugin in self.enabled()
            if capability in plugin.metadata().capabilities
        ]

    def health(self) -> List[dict]:
        return [plugin.health() for plugin in self.all()]
