# READONLY_AUDIT Request — OES-007 / OES-RC-0004-R1

Solicito auditoria técnica em modo READONLY_AUDIT do OES-007 / OES-RC-0004-R1.

## Contexto

O OES-006 / RC-0003-R3 foi publicado e aprovado como base do catálogo de 56 capabilities. Este novo RC projeta contratos e eventos primários a partir dessas capabilities, sem alterar runtime, API, banco ou infraestrutura.

## Escopo obrigatório

1. Confirmar integridade do pacote.
2. Validar manifesto SHA-256.
3. Confirmar 56/56 capabilities projetadas.
4. Confirmar 56 command contracts únicos.
5. Confirmar 56 primary events únicos.
6. Confirmar fechamento vocabular contra `reference_vocabulary.json`.
7. Confirmar ausência de referências não canônicas.
8. Confirmar ausência de arquivos fora de `/specification`.
9. Confirmar ausência de alterações em runtime/API/banco/infra.
10. Classificar estado final como GREEN / YELLOW / RED.

## Restrições

- Não alterar arquivos.
- Não corrigir automaticamente.
- Não realizar commit.
- Não realizar push.
- Não abrir PR.
- Não fazer deploy.
- Apenas auditar, comparar e reportar.

## Resultado esperado

Parecer final GO / NO-GO para merge/manual upload.
