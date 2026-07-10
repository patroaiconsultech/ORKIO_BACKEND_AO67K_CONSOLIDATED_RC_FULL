FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# AO-01 BOOT NAMESPACE FIX
# The consolidated repo is checked out at /app, while the application is imported as app.main.
# PYTHONPATH=/ and --app-dir / force Python/Uvicorn to resolve:
# app -> /app
# app.main -> /app/main.py
# app.runtime -> /app/runtime
ENV PYTHONPATH=/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# AO-01 CACHE BUST
# Bump this value whenever a clean Railway rebuild is required.
ARG CACHEBUST=2026-07-10T_NAMESPACE_FIX_02

COPY . .

# Railway injects PORT. Do NOT hardcode.
# Production boot contract:
# 1) validate Alembic state
# 2) apply migrations
# 3) validate the Python package namespace
# 4) start Uvicorn with an explicit application directory
CMD ["sh","-c","python scripts/preflight_alembic_version.py && alembic upgrade head && cd / && python /app/scripts/preflight_python_namespace.py && python -m uvicorn --app-dir / --log-config /app/logging_uvicorn_stdout.json app.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE:-75}"]
