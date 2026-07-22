# AO-01 Runtime Facade Restore

## Finding
The two `capability_registry.py` files are byte-for-byte identical.

SHA-256:

```text
0b2ace9400b270af918ba3789415eb3c32e5c6bbc37a9d9ed1d3597de135c96b
```

The regression is exclusively in `app/runtime/__init__.py`:

- historical file: exports the runtime facade expected by `app.main`
- current file: contains only a package docstring

## Apply

Replace:

```text
app/runtime/__init__.py
```

with the included file.

Do not replace `capability_registry.py`; both supplied versions are identical.

## Validate

```bash
python -m py_compile app/runtime/__init__.py
PYTHONPATH=/ python -c "from app.runtime import get_capability_registry; print('RUNTIME_IMPORT_OK', len(get_capability_registry()))"
PYTHONPATH=/ python smoke_runtime_facade.py
PYTHONPATH=/ python -c "import app.main; print('ORKIO_MAIN_IMPORT_OK')"
```

## Expected

```text
RUNTIME_IMPORT_OK ...
ORKIO_RUNTIME_FACADE_OK ...
ORKIO_MAIN_IMPORT_OK
```

## Rollback

Restore the previous `app/runtime/__init__.py`.
