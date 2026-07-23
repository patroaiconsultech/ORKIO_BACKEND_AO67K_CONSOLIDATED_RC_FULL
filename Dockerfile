FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Namespace híbrido controlado:
# - "/" permite que /app seja resolvido como o pacote Python "app";
# - "/app" preserva imports absolutos legados como runtime, services e config.
#
# ATENÇÃO:
# O diretório de trabalho não pode ser /app durante a validação de "app.*",
# pois /app/app sombrearia o pacote raiz /app.
ENV PYTHONPATH=/:/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Invalida explicitamente as camadas posteriores deste diagnóstico.
ARG CACHEBUST=2026-07-23T_AO01_NAMESPACE_R18
RUN echo "ORKIO_CACHEBUST=${CACHEBUST}"

COPY . .

# Validação estrutural e de namespace.
#
# A execução parte de "/" de forma intencional:
# - app              -> /app/__init__.py
# - app.main         -> /app/main.py
# - app.runtime      -> /app/runtime/__init__.py
# - runtime          -> /app/runtime/__init__.py (compatibilidade legada)
RUN cd / && PYTHONPATH=/:/app python - <<'PY'
from pathlib import Path
import importlib
import importlib.util
import os
import sys

EXPECTED_APP_INIT = Path("/app/__init__.py").resolve()
EXPECTED_RUNTIME_INIT = Path("/app/runtime/__init__.py").resolve()

print("=" * 80)
print("ORKIO BUILD NAMESPACE DIAGNOSTIC R18")
print("=" * 80)
print("PWD:", os.getcwd())
print("SYS.PATH:")
for item in sys.path:
    print(" -", item)

required_paths = [
    Path("/app"),
    Path("/app/__init__.py"),
    Path("/app/main.py"),
    Path("/app/runtime"),
    Path("/app/runtime/__init__.py"),
    Path("/app/runtime/capability_registry.py"),
    Path("/app/scripts/preflight_python_namespace.py"),
]

print("FILESYSTEM:")
for path in required_paths:
    print(
        f" - {path}: "
        f"exists={path.exists()} dir={path.is_dir()} file={path.is_file()}"
    )

missing_paths = [str(path) for path in required_paths if not path.exists()]
if missing_paths:
    raise SystemExit(f"ORKIO_REQUIRED_PATHS_MISSING: {missing_paths}")

root_init = Path("/app/__init__.py")
expected_root_init = '"""ORKIO backend application package."""'
actual_root_init = root_init.read_text(encoding="utf-8").strip()

print("ORKIO_ROOT_INIT_CONTENT:", repr(actual_root_init))

if actual_root_init != expected_root_init:
    raise SystemExit(
        "ORKIO_ROOT_INIT_INVALID: "
        f"expected={expected_root_init!r} actual={actual_root_init!r}"
    )

for module_name in ("app", "app.main", "app.runtime", "runtime"):
    try:
        spec = importlib.util.find_spec(module_name)
    except Exception as exc:
        spec = f"ERROR: {exc!r}"
    print(f"FIND_SPEC({module_name!r}):", spec)

app_module = importlib.import_module("app")
app_origin = Path(app_module.__file__).resolve()
print("APP_IMPORT_OK:", app_origin)

if app_origin != EXPECTED_APP_INIT:
    raise SystemExit(
        "ORKIO_APP_NAMESPACE_SHADOWED: "
        f"expected={EXPECTED_APP_INIT} actual={app_origin}"
    )

runtime_module = importlib.import_module("app.runtime")
runtime_origin = Path(runtime_module.__file__).resolve()
print("APP_RUNTIME_IMPORT_OK:", runtime_origin)

if runtime_origin != EXPECTED_RUNTIME_INIT:
    raise SystemExit(
        "ORKIO_APP_RUNTIME_NAMESPACE_INVALID: "
        f"expected={EXPECTED_RUNTIME_INIT} actual={runtime_origin}"
    )

legacy_runtime = importlib.import_module("runtime")
print("LEGACY_RUNTIME_IMPORT_OK:", Path(legacy_runtime.__file__).resolve())

required_exports = [
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

missing_exports = [
    name for name in required_exports
    if not hasattr(runtime_module, name)
]

if missing_exports:
    raise SystemExit(
        f"ORKIO_RUNTIME_FACADE_MISSING: {missing_exports}"
    )

print("ORKIO_RUNTIME_FACADE_BUILD_OK:", len(required_exports))
print("ORKIO_BUILD_NAMESPACE_DIAGNOSTIC_OK_R18")
PY

# Contrato de inicialização:
# 1) validar o plano de migração;
# 2) validar a revisão Alembic;
# 3) aplicar migrations a partir de /app;
# 4) voltar para "/" antes de validar/importar o pacote app;
# 5) iniciar Uvicorn com PID 1 via exec.
CMD ["sh", "-c", "set -eu; export PYTHONPATH=/:/app; echo ORKIO_BOOT_START; python /app/scripts/preflight_migration_plan.py; python /app/scripts/preflight_alembic_version.py; cd /app; alembic upgrade head; cd /; python /app/scripts/preflight_python_namespace.py; exec python -m uvicorn --app-dir / --log-config /app/logging_uvicorn_stdout.json app.main:app --host 0.0.0.0 --port \"${PORT:-8080}\" --timeout-keep-alive \"${UVICORN_TIMEOUT_KEEP_ALIVE:-75}\""]
