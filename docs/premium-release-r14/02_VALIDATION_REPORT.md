# Relatório de validação R1.4

## Artefato pai

```text
filename=ORKIO_BACKEND_PREMIUM_R13_ROOT_UPLOAD.zip
sha256=e2b0bfbe974b4081337af6a194f2e13db85c514803fac0ad8c8538e8502522d6
git_metadata_present=false
branch=NOT_PROVEN
commit=NOT_PROVEN
deployed_commit=NOT_PROVEN
```

## Compilação e testes

```text
python_compile_all=PASS
python_files=566
focused_tests=37 passed
full_suite=296 passed, 7 failed, 4 skipped
new_failures=0
```

As sete falhas são preexistentes e permanecem nas mesmas áreas:

```text
2 x AO-01 route diagnostics
3 x DOCIO payload/bridge
2 x document artifact rendering
```

## Cenários de governança reproduzidos

```text
production + policy ausente=PASS_BLOCK_WITHOUT_DDL
staging + auto=true + normalization ausente=PASS_BLOCK_WITHOUT_DDL
staging + auto=true + normalization=true=PASS_CONTROLLED_CREATE
production + auto=false + synchronized=PASS_READONLY_CONTINUE
```

## Boot controlado

```text
app.main import=PASS
FastAPI startup=PASS
route_count=253
/health=200 degraded_without_database
/api/health=200 degraded_without_database
runtime_identity_status=validated
runtime_identity_validated=true
```

A degradação de health decorre da ausência deliberada de PostgreSQL neste
ambiente, não de falha de import ou startup.

## Limitações

```text
real_postgresql=NOT_EXECUTED
railway_runtime=NOT_EXECUTED
live_sse_provider=NOT_EXECUTED
two_tenant_postgresql=NOT_EXECUTED
git_baseline_correlation=NOT_PROVEN
```
