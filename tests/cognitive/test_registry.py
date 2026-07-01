import pytest

from app.cognitive.plugins.intent import CoreIntentPlugin
from app.cognitive.registry import PluginRegistry


def test_registry_rejects_duplicate_plugin_names():
    registry = PluginRegistry()
    registry.register(CoreIntentPlugin())

    with pytest.raises(ValueError):
        registry.register(CoreIntentPlugin())


def test_registry_filters_by_capability():
    registry = PluginRegistry()
    registry.register(CoreIntentPlugin())

    plugins = registry.by_capability("intent")

    assert len(plugins) == 1
    assert plugins[0].metadata().name == "core.intent"
