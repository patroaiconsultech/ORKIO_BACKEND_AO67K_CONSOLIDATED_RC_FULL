# Validation report

## Compilation

```text
python_files_compiled=588
compile_errors=0
```

## Evolution Intelligence tests

```text
focused_r16_tests=27 passed
existing_evolution_tests=34 passed, 2 skipped
```

The skipped tests require real PostgreSQL.

## Full suite

```text
323 passed
7 failed
4 skipped
new_failures=0
```

The seven failures are the historical baseline failures already present in
R1.4/R1.5:

```text
2 AO-01 route diagnostics
3 DOCIO payload/bridge
2 document artifact rendering
```

## Migration validation

```text
0038 → 0039 → 0040 targeted SQLite upgrade=PASS
0040 → 0039 targeted downgrade=PASS
new tables=PASS
immutable triggers=PASS
target history constraints=PASS
```

The historical migration chain contains PostgreSQL-specific operations.
Real PostgreSQL staging remains mandatory.

## Runtime validation

```text
app.main import=PASS
FastAPI startup=PASS
evolution_intelligence_status=validated
evolution_governance_validated=true
evolution_version=ORKIO-EVOLUTION-INTELLIGENCE-R1.1
route_count=272
/health=200
```

Unsafe configuration test:

```text
EVOLUTION_WRITE_ENABLED=true
startup=BLOCKED
error=EVOLUTION_GOVERNANCE_INVALID
```

## Limitations

```text
real_postgresql=NOT_EXECUTED
railway=NOT_EXECUTED
two_tenant_postgresql=NOT_EXECUTED
live_sse_provider=NOT_EXECUTED
frontend=NOT_INCLUDED
deploy=NOT_EXECUTED
production_migration=NOT_EXECUTED
```
