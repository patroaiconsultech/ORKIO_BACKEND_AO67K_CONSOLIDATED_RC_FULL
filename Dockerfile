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
ARG CACHEBUST=2026-07-21T_PREMIUM_NAMESPACE_RELID_MIGRATION_R14

COPY . .

# Railway injects PORT. Do NOT hardcode.
# Production boot contract:
# 1) inspect database revisions and enforce migration policy (readonly)
# 2) normalize the Alembic control table only with explicit authorization
# 3) apply application migrations only when the readonly policy permits
# 4) validate the Python package namespace
# 5) start Uvicorn with an explicit application directory
CMD ["sh","-c","python scripts/preflight_migration_plan.py && python scripts/preflight_alembic_version.py && alembic upgrade head && cd / && python /app/scripts/preflight_python_namespace.py && python -m uvicorn --app-dir / --log-config /app/logging_uvicorn_stdout.json app.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE:-75}"]
