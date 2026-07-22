# ORKIO Agent Evolution Map — R2.0

Read-only composition layer for the current cognitive state of ORKIO agents.

## Principles

- no database migration;
- no new source-of-truth registry;
- no write path;
- admin-only API;
- tenant scope derived by the backend;
- proposal-only governance;
- evidence and measurement metadata in every snapshot.

## Routes

- `GET /api/admin/evolution/agents`
- `GET /api/admin/evolution/agents/{agent_id}`
- `GET /api/admin/evolution/agents/{agent_id}/snapshot`
- `GET /api/admin/evolution/agents/{agent_id}/capabilities`
- `GET /api/admin/evolution/agents/{agent_id}/gaps`
- `GET /api/admin/evolution/agents/{agent_id}/dependencies`

Set `AGENT_EVOLUTION_MAP_ENABLED=false` to disable the routes.
