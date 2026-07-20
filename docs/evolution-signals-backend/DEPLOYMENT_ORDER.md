# Ordem de implantação

1. Criar branch a partir da `main` correspondente à produção `(41)`:

```text
evolution-signals-backend-v1-prod41
```

2. Extrair este ZIP.
3. Enviar todo o conteúdo extraído para a raiz da branch.
4. Revisar `main.py`: o diff deve mostrar somente 16 linhas adicionadas.
5. Executar:

```bash
python -m py_compile   main.py   routes/evolution_signals.py   schemas/evolution_signals.py   services/evolution_signal_service.py   alembic/versions/0037_patch_evolution_signals_metrics.py
```

```bash
python -m pytest -q   tests/test_evolution_signal_service.py   tests/test_evolution_signal_routes.py   tests/test_sec001_access_grants.py   tests/test_sec001_mutation_fail_closed.py
```

```bash
python -m alembic heads
```

Esperado:

```text
16 passed
0037_patch_evolution_signals_metrics (head)
```

6. Executar a suíte completa e comparar com o baseline `(41)`.
7. Abrir PR.
8. Fazer backup do banco.
9. Aplicar migration controlada:

```bash
python -m alembic upgrade 0037_patch_evolution_signals_metrics
```

10. Fazer deploy com:

```text
EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED=false
EVOLUTION_AGENT_EVAL_WRITE_ENABLED=false
ACCESS_GATE_REQUIRE_FOR_AUTH=false
```

11. Executar smoke readonly.
12. Não adaptar o frontend antes do GO do backend readonly.
