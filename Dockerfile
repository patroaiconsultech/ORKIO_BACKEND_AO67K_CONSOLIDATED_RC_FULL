FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# AO-01 BOOT NAMESPACE FIX
# The consolidated repo is checked out at /app, while the application is imported as app.main.
# PYTHONPATH=/:/app and --app-dir / support both package-style imports
# (app.main, app.runtime) and legacy repository-root imports
# (config, runtime, services) still present in the consolidated codebase.
# This is a compatibility bridge; new code should prefer app.* or relative imports.
ENV PYTHONPATH=/:/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# AO-01 CACHE BUST
# Bump this value whenever a clean Railway rebuild is required.
ARG CACHEBUST=2026-07-23T_ROOT_INIT_FIX_R15

COPY . .

# AO-01 BUILD-TIME PACKAGE VALIDATION
# Confirms that the root package file copied into the image is the expected one.
RUN python - <<'PY'
from pathlib import Path

root_init = Path("/app/__init__.py")
expected = '"""ORKIO backend application package."""'

if not root_init.is_file():
    raise SystemExit(f"ORKIO_ROOT_INIT_MISSING: {root_init}")

content = root_init.read_text(encoding="utf-8").strip()

print("ORKIO_ROOT_INIT_PATH", root_init)
print("ORKIO_ROOT_INIT_CONTENT", repr(content))

if content != expected:
    raise SystemExit(
        "ORKIO_ROOT_INIT_INVALID\n"
        f"path={root_init}\n"
        f"expected={expected!r}\n"
        f"actual={content!r}"
    )

print("ORKIO_ROOT_INIT_BUILD_OK")
PY

# AO-01 RUNTIME FACADE VALIDATION
# Ensures that app.runtime resolves and exposes the symbols required by app.main.
RUN PYTHONPATH=/:/app python - <<'PY'
import app.runtime as runtime

required = [
    "get_capability_registry",
    "build_intent_package",
    "build_first_win_plan",
    "build_continuity_hints",
    "build_arcangelic_chain",
    "build_system_overlay",
    "build_runtime_hints",
    "build_trial_hints",
    "build_planner_snapshot",
    "score_memory_candidate",
    "build_memory_snapshot",
    "build_trial_analytics",
    "build_dag_execution_snapshot",
]

missing = [name for name in required if not hasattr(runtime, name)]

if missing:
    raise SystemExit(f"ORKIO_RUNTIME_FACADE_MISSING: {missing}")

print("ORKIO_RUNTIME_FACADE_BUILD_OK", len(required))
PY

# Railway injects PORT. Do NOT hardcode.
# Production boot contract:
# 1) inspect database revisions and enforce migration policy (readonly)
# 2) normalize the Alembic control table only with explicit authorization
# 3) apply application migrations only when the readonly policy permits
# 4) validate the Python package namespace
# 5) start Uvicorn with an explicit application directory
CMD ["sh","-c","python scripts/preflight_migration_plan.py && python scripts/preflight_alembic_version.py && alembic upgrade head && cd / && python /app/scripts/preflight_python_namespace.py && exec python -m uvicorn --app-dir / --log-config /app/logging_uvicorn_stdout.json app.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE:-75}"]
