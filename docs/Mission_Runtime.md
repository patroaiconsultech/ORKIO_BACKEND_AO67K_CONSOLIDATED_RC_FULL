# Mission Runtime

## Purpose
Mission Runtime coordinates Orkio OS around the user's active objective.

It answers: **What mission is Orkio helping the user advance?**

## Mission State
```yaml
mission:
  id:
  title:
  objective:
  stage:
  domain:
  confidence:
  facts:
  hypotheses:
  open_questions:
  risks:
  next_best_action:
  progress:
```

## Responsibilities
- Detect or create active mission
- Maintain mission stage
- Connect conversation turns to objective
- Coordinate Cognitive Core with Experience Core
- Expose progress when appropriate
- Preserve continuity across sessions when allowed
- Respect Governance Core rules

## Mission Principle
Every strategic conversation should leave the mission clearer, safer or closer to execution.
