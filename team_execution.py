# AO-01 Premium Agent + Document + Team Patch

## Corrige

1. `source_plan` causando `extra_forbidden` em `DocumentArtifactGenerateIn`.
2. Menção explícita `@Chris`, `@Orion`, `@Laura` ou `@Orkio` sem ownership real.
3. Ponte documental usando Orkio mesmo quando outro agente foi solicitado.
4. `@Team` simulando múltiplos pontos de vista em uma única resposta.
5. Falha documental encerrando todo o turno de chat.

## Ordem de aplicação

1. Copiar `orkio_patches/` para a raiz do backend.
2. Aplicar `patches/app_main.integration.patch` por âncoras.
3. Aplicar `patches/team_runtime.integration.patch` no branch que trata `requested_agent == "team"`.
4. Executar os testes.
5. Homologar com os três comandos abaixo.

## Testes de aceitação

### Agente explícito

`@Chris, faça um breve resumo do documento enviado.`

Esperado:

- `requested_agent=chris`
- `turn_owner=chris`
- `display_agent=chris`
- `ownership_locked=true`
- resposta persistida com `agent_id=chris`

### Team real

`@Team, analisem o documento e respondam individualmente.`

Esperado:

- quatro `task_id`
- quatro `agent_result`
- quatro `result_artifact_id`
- nenhum ponto de vista inventado por Orkio
- cada bloco identificado pelo agente executor

### Documento

`Gere um .md com base no documento enviado.`

Esperado:

- `DocumentArtifactGenerateIn` validado
- nenhum erro `source_plan extra_forbidden`
- `artifact_created=true`, ou fallback textual seguro
- `event: done`

## Rollback

Remover os imports de `orkio_patches`, restaurar os três blocos anteriores e desativar:

- `EXPLICIT_AGENT_OWNERSHIP_V2`
- `TEAM_REAL_AGENT_EXECUTION_V1`
- `DOCIO_STRICT_PAYLOAD_V2`
- `DOCIO_FAIL_SOFT_V1`

Sem migration.
