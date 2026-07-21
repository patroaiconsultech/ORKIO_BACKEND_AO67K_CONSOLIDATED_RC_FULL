# Frontend patch contract

Arquivo provável:
- `src/components/BetaAccessGate.jsx`
- ou o componente equivalente que mostra “Validando sua autorização com segurança...”

Regra mínima:
1. Ler `mode` da URL.
2. Bypassar completamente consulta `/api/access-grants/status` em login, forgot e reset.
3. Consultar status e mostrar código somente quando `mode=register`.
4. Ao trocar de login para cadastro, iniciar o gate.
5. Ao trocar de cadastro para login, desmontar o gate e limpar apenas estado visual; não expor nem persistir código bruto.

Pseudodiff:

```diff
+ const authMode = new URLSearchParams(window.location.search).get("mode") || "login";
+ const requiresSpecialCode = authMode === "register";

- useEffect(() => { checkGrantStatus(); }, []);
+ useEffect(() => {
+   if (!requiresSpecialCode) {
+     setChecking(false);
+     setGranted(true);
+     return;
+   }
+   checkGrantStatus();
+ }, [requiresSpecialCode]);

+ if (!requiresSpecialCode) return children;
```

Não aplique este pseudodiff cegamente. Ajuste aos nomes reais do componente atual.
