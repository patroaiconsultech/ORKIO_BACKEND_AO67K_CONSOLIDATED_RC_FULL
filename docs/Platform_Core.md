# Platform Core

## Purpose
Platform Core is the operational foundation of Orkio OS 1.0.

It answers: **How does Orkio run?**

## Responsibilities
- FastAPI backend
- Runtime services
- SSE and streaming
- Auth and tenant boundaries
- Database and persistence
- Agents infrastructure
- Connectors
- Health checks
- Metrics
- Observability events
- Security foundation
- Operational readiness

## Non-goals
Platform Core must not define Orkio's cognitive behavior directly.

## Production Rule
Any Platform Core change must preserve baseline stability, regression compatibility, rollback capacity and operational visibility.
