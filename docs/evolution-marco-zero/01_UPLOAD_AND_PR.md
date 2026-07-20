# Upload e PR

## Branch

```text
mz001-r1-preview-only-prod42
```

## Upload

Extraia o ZIP e envie todo o conteúdo para a raiz do repositório backend.

## Commit sugerido

```text
fix(evolution): make marco zero tenant-bound and preview-only
```

## Título do PR

```text
MZ-001-R1: tenant-bound preview-only marco zero
```

## Revisão obrigatória

O diff deve alterar somente:

```text
main.py
tests/test_evolution_marco_zero_static.py
tests/test_evolution_marco_zero_preview.py
docs/evolution-marco-zero/*
```

Não há migration neste pacote.

## Ordem

```text
branch
→ upload
→ py_compile
→ testes focais
→ suíte completa CI
→ review
→ merge autorizado
→ deploy backend
→ habilitar preview
→ Gate R1
```
