# Release gates

## Branch and PR

```text
GO
```

provided the branch starts from the current backend HEAD and the cumulative
delta is reviewed as a normal Git diff.

## Staging

```text
GO_CONDITIONAL
```

Conditions:

- explicit migration policy;
- backup or isolated database;
- migration 0039 and 0040 review;
- real PostgreSQL smoke;
- two-tenant isolation;
- runtime governance consistency;
- immutable trigger verification.

## Production

```text
NO-GO
```

until:

- deployed commit is correlated;
- PostgreSQL migrations are synchronized;
- auth and thread visibility pass;
- tenant isolation passes;
- selected-agent ownership passes;
- SSE terminal contract passes;
- rollback is proven.

## Evolution writes

```text
NO-GO
```

Keep code write and auto-apply disabled.
