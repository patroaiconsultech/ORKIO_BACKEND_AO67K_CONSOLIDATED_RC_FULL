FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Compatibilidade temporária:
# / permite importar o pacote como app.main e app.runtime.
# /app preserva imports legados como config, runtime e services.
ENV PYTHONPATH=/:/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Alterar este valor força invalidação das camadas seguintes.
ARG CACHEBUST=2026-07-23T_AO01_NAMESPACE_DIAGNOSTIC_R17
RUN echo "ORKIO_CACHEBUST=${CACHEBUST}"

COPY . .

# Diagnóstico estrutural e de namespace durante o build.
RUN PYTHONPATH=/:/app python - <<'PY'
from pathlib import Path
import importlib.util
import os
import sys

print("=" * 80)
print("ORKIO BUILD NAMESPACE DIAGNOSTIC R17")
print("=" * 80)
print("PWD:", os.getcwd())
print("SYS.PATH:")
for item in sys.path:
    print(" -", item)

paths = [
    Path("/app"),
    Path("/app/__init__.py"),
    Path("/app/main.py"),
    Path("/app/runtime"),
    Path("/app/runtime/__init__.py"),
    Path("/app/runtime/capability_registry.py"),
]

print("FILESYSTEM:")
for path in paths:
    print(f" - {path}: exists={path.exists()} dir={path.is_dir()} file={path.is_file()}")

root_init = Path("/app/__init__.py")
expected = '"""ORKIO backend application package."""'

if not root_init.is_file():
    raise SystemExit("ORKIO_ROOT_INIT_MISSING: /app/__init__.py")

actual = root_init.read_text(encoding="utf-8").strip()
print("ORKIO_ROOT_INIT_CONTENT:", repr(actual))

if actual != expected:
    raise SystemExit(
        f"ORKIO_ROOT_INIT_INVALID: expected={expected!r} actual={actual!r}"
    )

for module_name in ("app", "runtime", "app.runtime"):
    try:
        spec = importlib.util.find_spec(module_name)
    except Exception as exc:
        spec = f"ERROR: {exc!r}"
    print(f"FIND_SPEC({module_name!r}):", spec)

import app
print("APP_IMPORT_OK:", getattr(app, "__file__", None))

import app.runtime as runtime
print("APP_RUNTIME_IMPORT_OK:", getattr(runtime, "__file__", None))

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

print("ORKIO_RUNTIME_FACADE_BUILD_OK:", len(required))
print("ORKIO_BUILD_NAMESPACE_DIAGNOSTIC_OK")
PY

# Contrato de inicialização:
# 1) validar plano de migração;
# 2) validar revisão Alembic;
# 3) aplicar migrations;
# 4) validar namespace Python no ambiente final;
# 5) iniciar Uvicorn.
CMD ["sh", "-c", "set -eu; export PYTHONPATH=/:/app; echo ORKIO_BOOT_START; python /app/scripts/preflight_migration_plan.py; python /app/scripts/preflight_alembic_version.py; cd /app; alembic upgrade head; cd /; python /app/scripts/preflight_python_namespace.py; exec python -m uvicorn --app-dir / --log-config /app/logging_uvicorn_stdout.json app.main:app --host 0.0.0.0 --port \"${PORT:-8080}\" --timeout-keep-alive \"${UVICORN_TIMEOUT_KEEP_ALIVE:-75}\""]
