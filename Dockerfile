FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/:/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ARG CACHEBUST=2026-07-23T_RUNTIME_DIAGNOSTIC_R16

COPY . .

# Validação do __init__.py da raiz
RUN python - <<'PY'
from pathlib import Path

root_init = Path("/app/__init__.py")
expected = '"""ORKIO backend application package."""'

if not root_init.exists():
    raise SystemExit(f"ORKIO_ROOT_INIT_MISSING: {root_init}")

content = root_init.read_text(encoding="utf-8").strip()

print("ORKIO_ROOT_INIT_PATH:", root_init)
print("ORKIO_ROOT_INIT_CONTENT:", repr(content))

if content != expected:
    raise SystemExit(
        f"ORKIO_ROOT_INIT_INVALID\nEsperado={expected!r}\nObtido={content!r}"
    )

print("ORKIO_ROOT_INIT_BUILD_OK")
PY

# Diagnóstico de namespace Python
RUN PYTHONPATH=/:/app python - <<'PY'
import os
import sys
import importlib.util

print("=" * 80)
print("ORKIO PYTHON DIAGNOSTIC")
print("=" * 80)

print("PWD:")
print(os.getcwd())

print("\nSYS.PATH:")
for p in sys.path:
    print(" ", p)

print("\nFIND_SPEC(app):")
print(importlib.util.find_spec("app"))

print("\nFIND_SPEC(runtime):")
print(importlib.util.find_spec("runtime"))

print("\nTRY IMPORT app")
try:
    import app
    print("OK:", app)
    print("FILE:", getattr(app, "__file__", None))
except Exception as e:
    print("ERROR:", repr(e))

print("\nTRY IMPORT runtime")
try:
    import runtime
    print("OK:", runtime)
    print("FILE:", getattr(runtime, "__file__", None))
except Exception as e:
    print("ERROR:", repr(e))

print("\nTRY IMPORT app.runtime")
try:
    import app.runtime
    print("OK")
except Exception as e:
    print("ERROR:", repr(e))
    raise
PY

CMD ["sh","-c","python scripts/preflight_migration_plan.py && python scripts/preflight_alembic_version.py && alembic upgrade head && cd / && python /app/scripts/preflight_python_namespace.py && exec python -m uvicorn --app-dir / --log-config /app/logging_uvicorn_stdout.json app.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE:-75}"]
