from app.runtime import (
    get_capability_registry,
    build_intent_package,
    build_first_win_plan,
    build_continuity_hints,
    build_arcangelic_chain,
    build_system_overlay,
    build_runtime_hints,
    build_trial_hints,
    build_planner_snapshot,
    score_memory_candidate,
    build_memory_snapshot,
    build_trial_analytics,
    build_dag_execution_snapshot,
)

registry = get_capability_registry()
assert isinstance(registry, dict)
assert "orkio" in registry
print("ORKIO_RUNTIME_FACADE_OK", len(registry))
