# ORKIO Evolution Intelligence Foundation R1.5

## Objetivo

Transformar os sinais já existentes do Evolution Center em uma fundação
confiável de objetivos, metas, saúde composta, diagnóstico, priorização e
propostas somente para revisão humana.

Esta release **não** aplica patches, não cria commits, não abre PRs, não executa
deploys e não habilita auto-apply.

## Escopo entregue

- catálogo formal e versionado dos sete sinais atuais;
- objetivos tenant-isolated, limitados a cinco ativos por tenant;
- metas globais ou vinculadas a objetivo;
- score de saúde por dimensão e score geral com cobertura;
- ausência de dados representada como `unknown` ou `insufficient_data`;
- blockers não compensáveis por média;
- diagnóstico que separa evidência de hipótese;
- priorização transparente;
- preview de proposta em `proposal_only`;
- snapshots compostos imutáveis, com escrita desabilitada por padrão;
- auditoria de alterações de objetivo, meta e snapshot;
- startup fail-closed para configurações inseguras;
- migration 0039 com constraints tenant-aware.

## Não incluído

- frontend;
- aplicação automática de proposta;
- geração de diff baseada em causa não confirmada;
- escrita em GitHub;
- execução em staging ou produção;
- validação PostgreSQL/Railway real;
- SSE real com provider.

## Ordem de aplicação

1. Criar branch a partir do HEAD atual.
2. Aplicar o pacote delta na raiz do backend.
3. Executar `python scripts/validate_premium_package.py`.
4. Executar `python scripts/evolution_validate_kpis.py`.
5. Revisar a migration 0039.
6. Configurar flags explicitamente.
7. Subir staging com PostgreSQL.
8. Executar `03_STAGING_SMOKE.md`.
9. Manter escrita e auto-apply desativados.
