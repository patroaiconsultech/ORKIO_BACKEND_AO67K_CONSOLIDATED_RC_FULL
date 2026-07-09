FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# AO68A BOOT NAMESPACE FIX
# The consolidated repo is checked out at /app, but the code imports modules as `app.*`
# and uses package-relative imports such as `.db`.
# Adding `/` to PYTHONPATH lets Python treat `/app` as the `app` namespace package.
ENV PYTHONPATH=/
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# MANUS_UX_R4_CACHE_BUST — Force Railway BuildKit to invalidate cache from this point.
# This ensures COPY picks up the latest main.py (52078 lines, SHA 5916ffe8).
# Bump the default value below on every deploy that needs cache invalidation.
ARG CACHEBUST=2026-07-09T16h30
COPY . .
# Railway injects PORT. Do NOT hardcode.
# Production boot contract:
# 1) apply Alembic preflight before the app starts
# 2) apply Alembic migrations before the app starts
# 3) fail fast if the database schema cannot be reconciled
# 4) then start the API
CMD ["sh","-c","python scripts/preflight_alembic_version.py && alembic upgrade head && uvicorn --log-config logging_uvicorn_stdout.json app.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE:-75}"]
