# ORKIO MCP Auditor Readonly - Security, RBAC and Risk Review

## Escopo de Segurança

Este desenho cobre somente o MCP Auditor readonly Fase 1.

Fora do escopo:

- MCP Dev;
- escrita em branch;
- aplicação de patch;
- geração automática de PR;
- deploy;
- migration;
- alteração de usuário;
- alteração de permissões globais;
- leitura de conteúdo integral de documento;
- leitura de mensagens integrais;
- acesso a secrets.

## Modelo de Ameaças

### Ameaça 1: Exposição de conteúdo bruto de mensagens

Mitigações:

- `queries.py` usa allowlist de colunas.
- Colunas com `content`, `body`, `text`, `raw`, `extract`, `chunk` e `embedding` são bloqueadas.
- Teste `test_no_content_leak.py` valida que conteúdo bruto não retorna mesmo quando a tabela contém essas colunas.

Risco residual:

- Nomes de colunas personalizados podem exigir ajuste de allowlist.

Controle obrigatório:

- Revisão humana da tabela real antes de habilitar.

### Ameaça 2: Exposição de conteúdo de documentos

Mitigações:

- `get_file_refs` retorna apenas referências.
- Filename é hash + extensão.
- Texto extraído, chunks e embeddings não são selecionados.

Risco residual:

- Metadados como MIME type e tamanho podem revelar categoria geral de arquivo.

Controle obrigatório:

- Validar política interna de exposição de metadados.

### Ameaça 3: Uso do MCP como canal de escrita

Mitigações:

- Apenas sete ferramentas readonly são registradas.
- RBAC bloqueia qualquer ferramenta fora de `READONLY_TOOLS`.
- Código de queries não contém operações de escrita em dados de produto.
- Credencial de banco deve ser readonly.

Risco residual:

- Dependência de configuração correta do banco.

Controle obrigatório:

- Criar usuário DB readonly para o MCP.
- Negar privilégios INSERT, UPDATE, DELETE, ALTER, DROP, TRUNCATE e CREATE.

### Ameaça 4: Acesso por cliente não autorizado

Mitigações:

- Servidor exige `ORKIO_MCP_AUDITOR_ENABLED=true` para operar.
- Documento exige autenticação externa obrigatória.
- RBAC exige role `readonly_auditor`.
- Escopo de organização é obrigatório.

Risco residual:

- MCP via stdio depende do controle do processo local.
- MCP remoto depende de gateway/conector autenticado.

Controle obrigatório:

- Não expor o servidor em rede pública.
- Usar VPN, gateway autenticado, SSO, reverse proxy autenticado ou conector com controle de acesso.

### Ameaça 5: Vazamento via logs

Mitigações:

- `get_recent_logs_sanitized` mascara e-mails, bearer tokens, cookies, senhas, tokens, JWTs, hex strings longas e query params sensíveis.
- `audit_trail.py` não grava argumentos brutos.

Risco residual:

- Logs podem conter formatos de segredo não previstos.

Controle obrigatório:

- Manter logs de origem com retenção mínima.
- Ampliar regex quando novos padrões forem encontrados.

### Ameaça 6: Cross-tenant leak

Mitigações:

- `authorize_tool` valida `org_id` contra `ORKIO_MCP_AUDITOR_ALLOWED_ORG_IDS`.
- Queries aplicam filtro de organização quando a coluna existe.
- User IDs e organization IDs retornam como hash.

Risco residual:

- Tabelas sem coluna de organização dependem de isolamento por thread_id.

Controle obrigatório:

- Validar schema real.
- Exigir org_id nas chamadas de inspeção em ambiente multi-tenant.

## RBAC

### Papéis

`readonly_auditor`

- Pode chamar as sete ferramentas readonly.
- Não pode escrever.
- Não pode aplicar patch.
- Não pode abrir PR.
- Não pode executar deploy.
- Não pode executar migration.
- Não pode ler secrets.

### Matriz de Permissão

| Ferramenta | readonly_auditor | Observação |
|---|---:|---|
| get_health | Sim | Sem secrets |
| get_recent_logs_sanitized | Sim | Sanitizado |
| get_thread_metadata | Sim | Metadata apenas |
| get_message_counts | Sim | Contagens apenas |
| get_file_refs | Sim | Refs sem conteúdo |
| get_runtime_flags | Sim | Valores sensíveis redigidos |
| get_audit_reports | Sim | Metadados apenas |
| apply_patch_to_branch | Não | MCP Dev fora do escopo |
| run_tests | Não | MCP Dev fora do escopo |
| generate_diff | Não | MCP Dev fora do escopo |
| prepare_pr | Não | MCP Dev fora do escopo |
| deploy | Não | Proibido |
| run_migration | Não | Proibido |

## Autenticação

Fase 1 recomenda autenticação externa obrigatória. O servidor MCP não deve ser publicado diretamente.

Opções aceitáveis:

- execução local via stdio em máquina administrativa controlada;
- conector MCP com autenticação do provedor;
- gateway privado com SSO;
- reverse proxy autenticado;
- VPN administrativa;
- rede privada de staging.

Opções não aceitáveis:

- endpoint público sem autenticação;
- bearer token hardcoded em repositório;
- secrets em `.env` versionado;
- credencial de banco com privilégios de escrita;
- exposição direta em produção.

## Audit Trail

Cada chamada deve registrar:

- `ts`;
- `correlation_id`;
- `principal_ref`;
- `role`;
- `tool`;
- `outcome`;
- `resource_refs`;
- erro sanitizado quando houver.

Não registrar:

- e-mail completo;
- senha;
- token;
- cookie;
- payload completo;
- mensagem completa;
- conteúdo de documento;
- connection string;
- stack trace com dados sensíveis.

## Plano de Testes

### Testes Unitários

- Sanitização de e-mail, token, cookie, senha, JWT e query params.
- Hash estável de identificadores.
- RBAC para ferramentas permitidas e negadas.
- Bloqueio de org fora de escopo.
- Contrato de retorno das tools.

### Testes Anti-vazamento

- Criar SQLite temporário com colunas proibidas.
- Inserir conteúdo bruto em `content` e `extracted_text`.
- Confirmar que as funções retornam apenas metadata, contagens e refs.
- Confirmar que filename é hash + extensão.

### Testes Manuais

- Chamar cada ferramenta em ambiente controlado.
- Conferir audit trail JSONL.
- Conferir que logs são sanitizados.
- Conferir que runtime flags sensíveis são redigidas.
- Conferir que org fora de escopo é negada.

## Rollback

Rollback é operacional e imediato:

1. Desabilitar `ORKIO_MCP_AUDITOR_ENABLED`.
2. Parar processo MCP.
3. Remover configuração do cliente MCP.
4. Revogar credencial readonly de banco criada para o MCP.
5. Arquivar audit trail local.
6. Confirmar que nenhum dado de produto foi alterado.

## Registro de Riscos

| ID | Risco | Severidade | Mitigação | Residual |
|---|---|---:|---|---|
| MCP-R1 | Servidor exposto sem autenticação externa | P0 | Gateway/SSO/VPN e enabled=false por padrão | Médio |
| MCP-R2 | DB user com privilégio de escrita | P0 | Usuário readonly e teste de privilégios | Baixo |
| MCP-R3 | Schema real com colunas inesperadas | P1 | Allowlist e revisão humana | Médio |
| MCP-R4 | Logs com segredo em formato desconhecido | P1 | Sanitizers e revisão incremental | Médio |
| MCP-R5 | Consulta sem org_id em ambiente multi-tenant | P1 | Escopo org obrigatório por política | Médio |
| MCP-R6 | Audit trail local inacessível ou sem retenção | P2 | Path dedicado e política de retenção | Baixo |
| MCP-R7 | Confusão com MCP Dev | P2 | Dev fora do pacote e RBAC sem ferramentas Dev | Baixo |

## Veredito Executivo

Tecnicamente viável para Fase 1 como MCP Auditor readonly.

Compatível com uso manual auditável em ambiente local ou staging administrativo.

NO-GO para produção até validação humana, credencial DB readonly, autenticação externa obrigatória e testes verdes.

MCP Dev permanece fora do escopo.
